# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | ✅        |
| 0.5.x   | ⚠️ security fixes only |
| < 0.5   | ❌        |

## Reporting a vulnerability

Email `security@realty-stage-ai-studio.dev` with:

- A minimal reproducer (photo + preset + command).
- Whether the issue is local-only or can be triggered by a
  malicious listing fixture / preset file.
- Your preferred credit line for the advisory.

We aim to acknowledge within 72h and ship a patch within 14 days for
high-severity issues.

## Threat model

This is a **local desktop tool**. It reads photos and preset files from
disk and writes staged renders. Realistic attack surface:

1. **Malicious preset files.** Presets are TOML + a small JSON
   sidecar. We parse with `tomllib` and a strict pydantic schema.
   Anything that fails schema is rejected — do not "tolerate" unknown
   keys in a preset parser.
2. **Malicious image files.** All decoding goes through
   `adapters/cv2_image.py`, which enforces a max pixel budget
   (`MAX_PIXELS = 80_000_000`) before decode to bound decompression
   bombs.
3. **Path traversal via `--out`.** Output paths are resolved and
   confined to the configured `output_root`. Symlinks are not
   followed on write.
4. **Model weight supply chain.** Weights are fetched with a pinned
   SHA-256 from `config/weights.lock.toml`. Never load a `.pt` that
   isn't in the lockfile without an explicit `--allow-unpinned`
   flag.

## Out of scope

- GPU driver bugs (report upstream).
- Staged renders being "unrealistic" — that's a quality issue, not a
  security one. File it as a normal bug.
- Anything requiring an attacker to already have code execution on
  the host.