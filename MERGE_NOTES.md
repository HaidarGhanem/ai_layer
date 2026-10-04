# Merge Notes

1. Copy the replacement files first.
2. Add the new `services/errors`, `services/api`, and `services/observability` packages.
3. Keep the existing `services/streaming` implementation.
4. Keep the existing `services/tools` implementation and the existing test tools under `services/loop/tools`.
5. Do not move or rename old tool files as part of this merge.
6. Do not add LangServe to the final V1 controller.
7. `Brain` now exposes `resume()` and `resume_stream()` in addition to `process()` and `stream()`.
8. When a Loop uses a checkpointer, the Brain uses `session_id` as LangGraph `thread_id`.
