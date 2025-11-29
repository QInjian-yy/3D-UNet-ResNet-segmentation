import torch
import sys

print("=" * 50)
print("PyTorch 和 CUDA 测试")
print("=" * 50)

print(f"Python版本: {sys.version}")
print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
print(f"CUDA版本: {torch.version.cuda}")

if torch.cuda.is_available():
    print(f"GPU数量: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    print(f"cuDNN版本: {torch.backends.cudnn.version()}")

    # 测试GPU计算
    device = torch.device('cuda')
    x = torch.randn(3, 3).to(device)
    print(f"GPU计算测试: 成功创建张量 {x.shape}")
else:
    print("警告: CUDA不可用，只能使用CPU")