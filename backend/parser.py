"""
Point Cloud Data Parser for NOVA-2.5D

Parses user-provided CSV and TXT point-cloud files with robust column detection,
missing-semantic tolerance, bounds extraction, and preview generation.
"""

import io
import re
import csv
import numpy as np


class PointCloudParseError(Exception):
    pass


def detect_delimiter(first_line: str) -> str:
    if "," in first_line:
        return ","
    if "\t" in first_line:
        return "\t"
    if ";" in first_line:
        return ";"
    return r"\s+"


def find_column_index(headers: list, candidates: list) -> int:
    clean_headers = [h.strip().lower().replace("_", "").replace("-", "") for h in headers]
    for candidate in candidates:
        clean_cand = candidate.lower().replace("_", "").replace("-", "")
        for idx, h in enumerate(clean_headers):
            if h == clean_cand:
                return idx
    return -1


def parse_point_cloud_text(content_bytes: bytes, filename: str = "upload.csv") -> dict:
    """
    Parses point cloud text into a structured NumPy array and metadata dict.
    Returns:
    {
        "points": np.ndarray of shape [N, 5] (x, y, z, intensity, semantic_class),
        "total_points": int,
        "has_semantics": bool,
        "columns_detected": list,
        "preview_rows": list of dicts,
        "bounds": { "x": [min, max], "y": [min, max], "z": [min, max] },
        "classes": list of { id, name, count, percentage }
    }
    """
    try:
        text = content_bytes.decode("utf-8", errors="replace").strip()
    except Exception as e:
        raise PointCloudParseError(f"Unable to decode file content: {str(e)}")

    if not text:
        raise PointCloudParseError("The uploaded file is empty.")

    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    if len(lines) < 5:
        raise PointCloudParseError(f"Insufficient data rows (found only {len(lines)} points). At least 10 points are required.")

    # Check first line for headers
    first_line = lines[0]
    delimiter = detect_delimiter(first_line)
    
    if delimiter == r"\s+":
        tokens = re.split(r"\s+", first_line)
    else:
        tokens = [t.strip() for t in first_line.split(delimiter)]

    # Test if tokens are floats or header strings
    has_header = False
    try:
        float(tokens[0])
    except ValueError:
        has_header = True

    data_lines = lines[1:] if has_header else lines
    header_tokens = tokens if has_header else [f"col_{i}" for i in range(len(tokens))]

    x_idx = find_column_index(header_tokens, ["x", "posx", "coordx"])
    y_idx = find_column_index(header_tokens, ["y", "posy", "coordy"])
    z_idx = find_column_index(header_tokens, ["z", "posz", "coordz", "elevation", "height"])
    intensity_idx = find_column_index(header_tokens, ["intensity", "i", "reflectance", "signal"])
    semantic_idx = find_column_index(header_tokens, ["semanticclass", "semantic", "class", "label", "category", "target"])

    num_cols = len(tokens)
    if not has_header:
        if num_cols >= 3:
            x_idx, y_idx, z_idx = 0, 1, 2
        if num_cols >= 4:
            intensity_idx = 3
        if num_cols >= 5:
            semantic_idx = 4

    if x_idx == -1 or y_idx == -1 or z_idx == -1:
        raise PointCloudParseError(
            f"Missing required coordinate columns. Detected headers: {header_tokens}. "
            "Please ensure 'x', 'y', and 'z' coordinates are provided."
        )

    # Parse rows
    parsed_points = []
    has_semantics = semantic_idx != -1
    malformed_count = 0

    for line in data_lines:
        if delimiter == r"\s+":
            parts = re.split(r"\s+", line)
        else:
            parts = [p.strip() for p in line.split(delimiter)]

        if len(parts) <= max(x_idx, y_idx, z_idx):
            malformed_count += 1
            continue

        try:
            x = float(parts[x_idx])
            y = float(parts[y_idx])
            z = float(parts[z_idx])
            intensity = float(parts[intensity_idx]) if (intensity_idx != -1 and intensity_idx < len(parts)) else 0.5
            sem = float(parts[semantic_idx]) if (has_semantics and semantic_idx < len(parts)) else 0.0
            parsed_points.append([x, y, z, intensity, sem])
        except ValueError:
            malformed_count += 1
            continue

    if len(parsed_points) < 5:
        raise PointCloudParseError(f"Could not parse valid 3D points. {malformed_count} malformed rows detected.")

    points_arr = np.array(parsed_points, dtype=np.float64)
    total_pts = len(points_arr)

    # Preview rows (up to 5)
    preview = []
    for i in range(min(5, total_pts)):
        p = points_arr[i]
        preview.append({
            "index": i,
            "x": round(float(p[0]), 3),
            "y": round(float(p[1]), 3),
            "z": round(float(p[2]), 3),
            "intensity": round(float(p[3]), 3),
            "semantic_class": int(p[4]) if has_semantics else None
        })

    # Bounds
    bounds = {
        "x": [round(float(np.min(points_arr[:, 0])), 2), round(float(np.max(points_arr[:, 0])), 2)],
        "y": [round(float(np.min(points_arr[:, 1])), 2), round(float(np.max(points_arr[:, 1])), 2)],
        "z": [round(float(np.min(points_arr[:, 2])), 2), round(float(np.max(points_arr[:, 2])), 2)],
    }

    # Semantic distribution if present
    classes = []
    if has_semantics:
        unique_classes, counts = np.unique(points_arr[:, 4], return_counts=True)
        class_name_map = {0: "Road/Ground", 1: "Vehicle", 2: "Pedestrian", 3: "Wall/Building", 4: "Noise/Other"}
        for cls_id, cnt in zip(unique_classes, counts):
            cls_int = int(cls_id)
            pct = round((cnt / total_pts) * 100, 1)
            classes.append({
                "id": cls_int,
                "name": class_name_map.get(cls_int, f"Class {cls_int}"),
                "count": int(cnt),
                "percentage": pct
            })

    detected_cols = ["x", "y", "z"]
    if intensity_idx != -1:
        detected_cols.append("intensity")
    if has_semantics:
        detected_cols.append("semantic_class")

    return {
        "points": points_arr,
        "total_points": total_pts,
        "has_semantics": has_semantics,
        "columns_detected": detected_cols,
        "preview_rows": preview,
        "bounds": bounds,
        "classes": classes,
        "malformed_rows_skipped": malformed_count
    }
