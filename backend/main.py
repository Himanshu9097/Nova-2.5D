"""
FastAPI Backend Application for NOVA-2.5D Input-Driven Benchmarking System
"""

import os
import sys
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from parser import parse_point_cloud_text, PointCloudParseError
from benchmark_runner import run_benchmark_suite
from history import load_history, add_history_entry, get_history_by_id, get_default_baseline

app = FastAPI(
    title="NOVA-2.5D Benchmark API",
    description="Backend service for input-driven 2.5D LiDAR benchmark evaluation",
    version="2.5.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_datasets")


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "NOVA-2.5D Benchmark Engine",
        "version": "2.5.0",
        "supported_formats": ["CSV", "TXT", "XYZ"]
    }


@app.get("/api/benchmark/samples")
def get_sample_datasets():
    samples = []
    if os.path.exists(SAMPLES_DIR):
        for fname in os.listdir(SAMPLES_DIR):
            if fname.endswith(".csv") or fname.endswith(".txt"):
                fpath = os.path.join(SAMPLES_DIR, fname)
                samples.append({
                    "filename": fname,
                    "size_bytes": os.path.getsize(fpath),
                    "name": fname.replace("sample_", "").replace(".csv", "").replace(".txt", "").replace("_", " ").title()
                })
    return {"samples": samples}


@app.post("/api/benchmark/validate")
async def validate_point_cloud(
    file: UploadFile = File(...)
):
    try:
        content = await file.read()
        parsed = parse_point_cloud_text(content, filename=file.filename)
        return {
            "valid": True,
            "filename": file.filename,
            "total_points": parsed["total_points"],
            "has_semantics": parsed["has_semantics"],
            "columns_detected": parsed["columns_detected"],
            "bounds": parsed["bounds"],
            "classes": parsed["classes"],
            "preview_rows": parsed["preview_rows"],
            "malformed_rows_skipped": parsed["malformed_rows_skipped"]
        }
    except PointCloudParseError as pe:
        raise HTTPException(status_code=400, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error validating file: {str(e)}")


@app.post("/api/benchmark/run")
async def run_benchmark(
    file: Optional[UploadFile] = File(None),
    sample_name: Optional[str] = Form(None),
    dataset_name: Optional[str] = Form("Uploaded Point Cloud"),
    uniform_resolution: float = Form(0.5),
    runs_count: int = Form(10)
):
    content = None
    resolved_name = dataset_name

    if file and file.filename:
        content = await file.read()
        resolved_name = file.filename if dataset_name == "Uploaded Point Cloud" else dataset_name
    elif sample_name:
        sample_path = os.path.join(SAMPLES_DIR, sample_name)
        if not os.path.exists(sample_path):
            raise HTTPException(status_code=404, detail=f"Sample dataset '{sample_name}' not found.")
        with open(sample_path, "rb") as f:
            content = f.read()
        resolved_name = sample_name.replace("sample_", "").replace(".csv", "").replace(".txt", "").replace("_", " ").title()
    else:
        raise HTTPException(status_code=400, detail="Please upload a point cloud file or select a sample dataset.")

    try:
        parsed = parse_point_cloud_text(content, filename=resolved_name)
        result = run_benchmark_suite(
            point_cloud=parsed["points"],
            dataset_name=resolved_name,
            uniform_resolution=uniform_resolution,
            runs_count=runs_count,
            has_semantics=parsed["has_semantics"]
        )

        # Attach parsed metadata and class breakdown
        result["dataset"]["bounds"] = parsed["bounds"]
        result["dataset"]["columns"] = parsed["columns_detected"]
        result["dataset"]["classes"] = parsed["classes"]
        result["dataset"]["preview"] = parsed["preview_rows"]

        # Save to persistent history
        run_id = add_history_entry(result)
        result["id"] = run_id

        return result

    except PointCloudParseError as pe:
        raise HTTPException(status_code=400, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {str(e)}")


@app.get("/api/benchmark/history")
def get_history():
    history = load_history()
    return {"history": history}


@app.get("/api/benchmark/history/{run_id}")
def get_single_history(run_id: str):
    entry = get_history_by_id(run_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"History entry '{run_id}' not found.")
    return entry


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
