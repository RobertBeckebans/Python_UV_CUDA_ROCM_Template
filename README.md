# TestPyTorch CUDA/ROCm with uv

This is an example project showing how to run PyTorch with NVIDIA (CUDA) and AMD (ROCm) GPUs using `uv`.

## Setup

This project uses `uv` extras to select the desired PyTorch backend.

### CPU (default)
```/dev/null/shell#L1-1
uv sync --extra cpu
```

### CUDA (Windows/Linux)
```/dev/null/shell#L1-1
uv sync --extra cuda
```

> **Note:** CUDA availability depends on your NVIDIA driver/runtime. If `CUDA available: False`, install a compatible driver and verify CUDA is visible to Python.

### ROCm (Linux only)
```/dev/null/shell#L1-1
uv sync --extra rocm
```

> **Note:** ROCm wheels are only available on Linux. On Windows, `uv sync --extra rocm` will fail because `pytorch-triton-rocm` is not published for Windows.

## Testing

Run the following command to verify your setup:

### CPU (default)
```/dev/null/shell#L1-1
uv run test_pytorch.py
```

### CUDA
```/dev/null/shell#L1-1
uv run --extra cuda test_pytorch.py
```

### ROCm (Linux only)
```/dev/null/shell#L1-1
uv run --extra rocm test_pytorch.py
```

## Troubleshooting

If you changed the PyTorch configuration and `uv` fails to resolve:
```/dev/null/shell#L1-2
rm uv.lock
uv sync --extra cpu
```
