# TestPyTorchCUDA/ROCm

## Setup

Copy or link the appropriate configuration file to `pyproject.toml` depending on your hardware:

- For CUDA: `pyproject_cuda.toml`
- For ROCm: `pyproject_rocm.toml`

## Testing

Run the following command to verify your setup:

```bash
uv run test_pytorch.py
```