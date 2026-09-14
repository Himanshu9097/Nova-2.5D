import torch_pointcloud as tp
import torch

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

try:
    model, info = tp.create_model(
        "randlanet.semantickitti.tsung-han-wu",
        task="segmentation",
        pretrained=True,
        return_info=True
    )
    print("Model loaded successfully!")
    print(f"Model info: {info}")
except Exception as e:
    print(f"Error loading model: {e}")
    import traceback
    traceback.print_exc()
