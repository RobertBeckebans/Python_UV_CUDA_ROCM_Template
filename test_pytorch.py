import torch

def print_torch_version():
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        print(f"Current GPU: {torch.cuda.get_device_name(0)}")
    
    # Check for ROCm
    if hasattr(torch.version, 'hip') and torch.version.hip is not None:
        print(f"ROCm/HIP available: True")
        print(f"ROCm version: {torch.version.hip}")
    else:
        print(f"ROCm/HIP available: False")
    
    # Device being used
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

if __name__ == "__main__":
    print_torch_version()