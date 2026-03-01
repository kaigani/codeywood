# ComfyUI Workflow API — Async Contract

Base URL: `http://192.168.1.181:8100`

The workflow API is **asynchronous**. Job submission returns immediately with a job ID. Poll for completion, then fetch the result.

---

## Endpoint Reference

### Health Check

```
GET /health
```

Response:
```json
{"status": "ok", "comfyui_reachable": true}
```

### List Workflows

```
GET /workflows
```

Returns array of workflow definitions with inputs, types, and defaults. See `references/services/comfyui/workflows.md` for full catalog.

### Submit Job

```
POST /workflows/{workflow_id}
Content-Type: application/x-www-form-urlencoded  (or multipart/form-data for file uploads)
```

Returns `202 Accepted`:
```json
{
  "job_id": "d0a39dbc523e49f0b6e9bb2ede0f280a",
  "status": "pending",
  "position": 1
}
```

- `position`: queue position (0 = next to run)
- Same form data and multipart file upload format as the old sync API

### Poll Job Status

```
GET /jobs/{job_id}
```

Response:
```json
{
  "job_id": "d0a39dbc523e49f0b6e9bb2ede0f280a",
  "workflow_id": "z-image-base-t2i",
  "status": "completed",
  "created_at": "2026-02-28T23:47:18.386433+00:00",
  "started_at": "2026-02-28T23:47:18.388175+00:00",
  "completed_at": "2026-02-28T23:47:18.816507+00:00",
  "error": null,
  "position": null
}
```

Fields:
| Field | Type | Notes |
|-------|------|-------|
| `job_id` | string | UUID hex |
| `workflow_id` | string | Which workflow was run |
| `status` | string | `pending`, `running`, `completed`, or `error` |
| `created_at` | string | ISO 8601 timestamp |
| `started_at` | string | null until running |
| `completed_at` | string | null until completed |
| `error` | string | null unless status is `error` |
| `position` | int | Queue position; null when running/completed |

Missing job returns `404`:
```json
{"detail": "Job not found: nonexistent-id"}
```

### Fetch Result

```
GET /jobs/{job_id}/result
```

- Returns binary data with correct `Content-Type` header (`image/png`, `video/mp4`, `audio/wav`, etc.)
- Only available when job status is `completed`
- PNG images include ComfyUI workflow metadata in tEXt chunk

### List All Jobs

```
GET /jobs
```

Returns array of job objects (same shape as single job poll).

---

## Status Lifecycle

```
pending  ──►  running  ──►  completed
                │
                └──►  error
```

- `pending`: Queued, waiting for GPU. `position` shows queue slot.
- `running`: Actively generating. `started_at` is set, `position` is null.
- `completed`: Done. `completed_at` is set. Result available at `/jobs/{id}/result`.
- `error`: Failed. `error` field contains the error message.

---

## Polling Pattern

Recommended approach:

| Phase | Interval | Rationale |
|-------|----------|-----------|
| First 5 polls | 2s | Catch fast jobs (small images, tiny params) |
| After 5 polls | 5s | Reduce load for longer jobs (video, high-step) |
| Timeout | 10 min | Safety net; longest jobs (LTX-2 201-frame video) take ~3-5 min |

Use `position` to estimate wait time when queued behind other jobs.

---

## Error Handling

| Scenario | How to detect |
|----------|---------------|
| Job failed | `status == "error"`, check `error` field for message |
| Job not found | HTTP 404 with `{"detail": "Job not found: ..."}` |
| Server down | `/health` returns non-200 or connection refused |
| ComfyUI unreachable | `/health` returns `{"comfyui_reachable": false}` |
| Result not ready | Don't call `/result` until `status == "completed"` |

---

## Migration: Sync → Async

### Old Pattern (sync — no longer works)
```python
resp = requests.post(url, data=params, timeout=600)
# resp.content was the binary result directly
with open("output.png", "wb") as f:
    f.write(resp.content)
```

### New Pattern (async)
```python
# 1. Submit
resp = requests.post(url, data=params)
job = resp.json()  # {"job_id": "...", "status": "pending", "position": N}

# 2. Poll
while True:
    status = requests.get(f"{base}/jobs/{job['job_id']}").json()
    if status["status"] in ("completed", "error"):
        break
    time.sleep(2)

# 3. Fetch result
if status["status"] == "completed":
    result = requests.get(f"{base}/jobs/{job['job_id']}/result")
    with open("output.png", "wb") as f:
        f.write(result.content)
```

---

## Python Polling Helper

```python
import time
import requests

COMFYUI_BASE = "http://192.168.1.181:8100"

def submit_and_wait(workflow_id, params, files=None, timeout=600, poll_interval=2):
    """Submit a workflow job, poll until done, return binary result.

    Args:
        workflow_id: e.g. "z-image-base-t2i", "ltx2-t2v"
        params: dict of form fields (prompt, seed, etc.)
        files: dict for multipart uploads, e.g. {"image": open("ref.png","rb")}
        timeout: max seconds to wait
        poll_interval: seconds between polls

    Returns:
        bytes: the result data (image/video/audio)

    Raises:
        TimeoutError: if job doesn't complete within timeout
        RuntimeError: if job fails with error
    """
    url = f"{COMFYUI_BASE}/workflows/{workflow_id}"

    if files:
        resp = requests.post(url, data=params, files=files)
    else:
        resp = requests.post(url, data=params)
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]

    deadline = time.time() + timeout
    while time.time() < deadline:
        status = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}").json()
        if status["status"] == "completed":
            result = requests.get(f"{COMFYUI_BASE}/jobs/{job_id}/result")
            return result.content
        if status["status"] == "error":
            raise RuntimeError(f"Job {job_id} failed: {status.get('error')}")
        time.sleep(poll_interval)

    raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")
```

Usage:
```python
# Text-to-image
png_bytes = submit_and_wait("z-image-base-t2i", {
    "prompt": "a sunset over the ocean",
    "seed": "42",
    "steps": "25",
    "width": "1024",
    "height": "1024",
})

# Image-to-video with file upload
with open("frame.png", "rb") as f:
    mp4_bytes = submit_and_wait("ltx2-i2v", {
        "prompt": "camera slowly pans right",
        "seed": "10",
        "frame_count": "121",
    }, files={"image": f}, timeout=300)

# Voice clone with audio file
with open("reference_voice.wav", "rb") as f:
    wav_bytes = submit_and_wait("qwen3-tts-voiceclone", {
        "text": "Hello, this is a cloned voice.",
    }, files={"voice": f})
```

---

## Endpoints That Do NOT Exist

These were probed and return 404:
- `/api/jobs` — not a valid path
- `/tasks` — not a valid path
- `/queue` — not a valid path
- `/jobs/{id}/status` — use `/jobs/{id}` instead (full job object)
