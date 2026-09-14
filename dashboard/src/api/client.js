/**
 * NOVA-2.5D Benchmark API Client
 * Connects frontend to the FastAPI backend service.
 */

const API_BASE_URL = 'http://127.0.0.1:8000';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (!res.ok) return { online: false };
    const data = await res.json();
    return { online: true, ...data };
  } catch (err) {
    return { online: false, error: err.message };
  }
}

export async function getSampleDatasets() {
  const res = await fetch(`${API_BASE_URL}/api/benchmark/samples`);
  if (!res.ok) throw new Error('Failed to fetch sample datasets');
  return res.json();
}

export async function validatePointCloudFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/api/benchmark/validate`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Validation failed' }));
    throw new Error(err.detail || 'Validation error');
  }

  return res.json();
}

export async function executeBenchmark({
  file = null,
  sampleName = null,
  datasetName = 'Uploaded Point Cloud',
  uniformResolution = 0.5,
  runsCount = 10
}) {
  const formData = new FormData();
  if (file) {
    formData.append('file', file);
  }
  if (sampleName) {
    formData.append('sample_name', sampleName);
  }
  formData.append('dataset_name', datasetName);
  formData.append('uniform_resolution', String(uniformResolution));
  formData.append('runs_count', String(runsCount));

  const res = await fetch(`${API_BASE_URL}/api/benchmark/run`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Benchmark execution failed' }));
    throw new Error(err.detail || 'Benchmark execution error');
  }

  return res.json();
}

export async function getBenchmarkHistory() {
  const res = await fetch(`${API_BASE_URL}/api/benchmark/history`);
  if (!res.ok) throw new Error('Failed to fetch benchmark history');
  return res.json();
}

export async function getSingleHistoryItem(runId) {
  const res = await fetch(`${API_BASE_URL}/api/benchmark/history/${runId}`);
  if (!res.ok) throw new Error('Failed to fetch historical benchmark run');
  return res.json();
}
