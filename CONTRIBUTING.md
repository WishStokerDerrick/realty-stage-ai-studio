# Contributing to realty-stage-ai-studio

Thanks for wanting to help stage houses with pixels instead of furniture.
This repo is a **service-oriented** Python desktop tool. Thin handlers,
fat services, one adapter per platform concern. If your PR fights that
shape, it will get bounced in review — not out of spite, out of
maintainability.

## Layout at a glance

```
realty-stage-ai-studio/
  bootstrap/        # entry points, CLI, app wiring
  handlers/         # thin request/event handlers (no business logic)
  services/         # business logic — staging, depth, inpaint, export
  adapters/         # platform + vendor boundaries (torch, cv2, mls, fs)
  models/           # domain dataclasses + pydantic schemas
  config/           # settings, presets, defaults
  utils/            # pure helpers — no I/O, no globals
  pipelines/        # composed service chains for full staging runs
  tests/            # pytest, mirrors the package tree
```

## Ground rules

1. **Handlers stay thin.** A handler validates input, calls one
   service, returns. If you're doing math in a handler, move it.
2. **Services never import adapters directly.** Services depend on the
   `adapters.*` protocols; the bootstrap wires concrete impls.
3. **No global model state.** Load weights through the
   `ModelRegistry` service; pass the handle down. Singleton weights
   loaded at import time will be rejected.
4. **Type hints required.** `mypy --strict` runs in CI. `Any` is a
   smell; use `Protocol` or a domain model.
5. **Determinism where possible.** Staging runs take a `seed` param.
   If your service ignores it, say why in the docstring.

## Dev setup

```bash
python -m venv .venv
. .venv/Scripts/activate      # Windows
pip install -e ".[dev]"
pre-commit install
pytest -q
```

## Commit style

Conventional-ish, lowercase, imperative:
`services/inpaint: clamp mask feather to <= 24px`
`adapters/torch: cache CUDA capability probe`

## PR checklist

- [ ] Tests added or updated under `tests/`
- [ ] `ruff check .` clean
- [ ] `mypy --strict realty_stage_ai` clean
- [ ] New presets documented in `config/presets/README.md`
- [ ] No new top-level deps without a justification paragraph

## Reporting bugs

Open an issue with: OS build, GPU + driver, `python -V`, the exact
`stage` command, and the input photo (or a redacted stand-in). Staging
bugs are almost always input-shape bugs — give us the shape.