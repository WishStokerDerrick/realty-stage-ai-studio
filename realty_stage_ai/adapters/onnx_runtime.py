"""ONNX Runtime adapter — the only place that touches onnxruntime directly."""
from __future__ import annotations

from pathlib import Path
from typing import Any


class OnnxRuntimeAdapter:
    def __init__(self, providers: list[str] | None = None) -> None:
        self._providers = providers or ["CUDAExecutionProvider", "CPUExecutionProvider"]

    def load(self, path: Path) -> Any:
        import onnxruntime as ort

        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.intra_op_num_threads = 0
        return ort.InferenceSession(str(path), sess_options=opts, providers=self._providers)