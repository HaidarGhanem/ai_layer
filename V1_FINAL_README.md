# AI Layer V1 — Final Remaining Layer

This package contains the final V1 layer that sits on top of the already-tested AI Core.

## Final V1 scope

Included:

- stable Core error taxonomy and normalization
- hardened Brain error boundaries
- synchronous Loop resume support
- FastAPI controller
- JSON process/resume APIs
- SSE stream/resume-stream APIs
- request IDs
- structured API errors
- LangSmith configuration/tracing bootstrap
- LangSmith evaluation dataset and runner
- deterministic API/error tests
- live final Core + API E2E test

Long-term memory is deliberately excluded from V1.

Odoo discovery/execution/permissions are deliberately excluded from this package and begin after V1 freeze.

## LangServe decision

The V1 controller is FastAPI-owned. LangServe is not used in the final controller architecture.

## Files to merge

Replace:

```text
services/brain/brain.py
services/loop/loop.py
services/loop/state.py
services/config.py
```

Add:

```text
services/brain/__init__.py
services/errors/*
services/api/*
services/observability/*
```

The existing `services/streaming`, `services/tools`, `services/context`, `services/RAG`, `services/LLM`, `services/retrieval`, `services/embedding`, `services/vectors`, and related Core modules remain unchanged.

Do not move the existing test tools under `services/loop/tools`.

## Install

The project already contains the main AI Core dependencies. Install only the remaining layer dependencies:

```powershell
venv\\Scripts\\python.exe -m pip install -r requirements-v1-remaining.txt
```

## Configuration

Copy:

```text
.env.example -> .env
```

LangSmith is optional for the deterministic tests and required only for the evaluation runner.

The live E2E test uses the existing local LLM/embedding setup. Make sure Ollama and the configured models are running.

## Test order

1. Error handling:

```powershell
venv\\Scripts\\python.exe v1_error_test.py
```

2. API contract without the real LLM:

```powershell
venv\\Scripts\\python.exe v1_api_test.py
```

3. Full live V1:

```powershell
venv\\Scripts\\python.exe v1_final_e2e_test.py
```

The final E2E covers Chat, RAG, Loop, tool execution, Brain streaming, risk confirmation, risk approval/rejection, FastAPI process, SSE, and HTTP confirmation/resume streaming.

## Start the API

```powershell
venv\\Scripts\\python.exe -m uvicorn run_api_demo:app --host 0.0.0.0 --port 8000
```

Routes:

```text
GET  /health
POST /v1/process
POST /v1/stream
POST /v1/resume
POST /v1/resume/stream
```

`/v1/stream` and `/v1/resume/stream` use the existing `StreamEvent` contract over SSE.

## LangSmith

Set:

```env
LANGSMITH_ENABLED=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=ai-layer-v1
```

Then:

```powershell
venv\\Scripts\\python.exe v1_langsmith_eval.py
```

The evaluation creates or reuses the `ai-layer-v1-core` dataset and checks:

- non-empty final content
- valid display type
- expected content when a deterministic expected substring is defined

`Brain.process` is traceable as a top-level Brain chain when LangSmith tracing is enabled, while the existing LangChain operations provide child traces.

## V1 freeze boundary

After these tests pass in the real project environment, V1 is considered functionally complete for the pre-Odoo phase.

Next phase:

```text
Odoo Discovery
→ Model / Field Catalog
→ Dynamic Tool Generation
→ Dynamic Executor
→ env.user permissions
→ Relational prerequisites
→ Change detection / indexing
→ Odoo integration E2E
```
