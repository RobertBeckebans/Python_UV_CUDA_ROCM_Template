# TestPyTorch CUDA/ROCm with uv

This is an example project showing how to run PyTorch with NVIDIA (CUDA) and AMD (ROCm) GPUs using `uv`.

## Setup

This project uses `uv` extras to select the desired PyTorch backend.

> **Python requirement:** Windows ROCm wheels from AMD are currently published for CPython 3.12, so this project targets Python 3.12 when using ROCm on Windows.

### CPU (default)
```/dev/null/shell#L1-1
uv sync --extra cpu
```

### CUDA (Windows/Linux)
```/dev/null/shell#L1-1
uv sync --extra cuda
```

> **Note:** CUDA availability depends on your NVIDIA driver/runtime. If `CUDA available: False`, install a compatible driver and verify CUDA is visible to Python.

### ROCm (Linux/Windows)
```/dev/null/shell#L1-1
uv sync --extra rocm
```

> **Note:** On Linux, wheels come from the official PyTorch ROCm index. On Windows, ROCm wheels are provided by AMD’s ROCm Windows repository and currently target CPython 3.12.

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

### ROCm (Linux/Windows)
```/dev/null/shell#L1-1
uv run --extra rocm test_pytorch.py
```

## Troubleshooting

If you changed the PyTorch configuration and `uv` fails to resolve:
```/dev/null/shell#L1-2
rm uv.lock
uv sync --extra cpu
```
