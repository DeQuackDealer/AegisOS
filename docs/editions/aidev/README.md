# Aegis OS AI Developer Edition

## Overview

Aegis OS AI Developer Edition is the ultimate platform for machine learning engineers, data scientists, and AI researchers. Pre-configured with GPU drivers, ML frameworks, and development tools, it eliminates the hours of setup typically required for AI development environments. Built on Arch Linux for access to the latest packages and rolling updates.

## Key Features

### GPU Computing Ready
- **NVIDIA CUDA Support** - Pre-installed drivers and CUDA toolkit
- **AMD ROCm Support** - OpenCL and HIP for AMD GPUs
- **Multi-GPU Configurations** - Train across multiple GPUs seamlessly
- **Tensor Core Optimization** - Automatic mixed precision support

### Pre-installed ML Frameworks
| Framework | Version | GPU Support |
|-----------|---------|-------------|
| PyTorch | Latest | CUDA, ROCm |
| TensorFlow | Latest | CUDA, ROCm |
| JAX | Latest | CUDA |
| ONNX Runtime | Latest | CUDA, TensorRT |
| Hugging Face | Latest | All backends |

### Development Environment
- **JupyterLab** - Interactive notebooks with GPU support
- **VS Code** - Pre-configured with Python, Jupyter extensions
- **tmux** - Terminal multiplexer for long training runs
- **Git LFS** - Large file storage for datasets and models

### Container & Virtualization
- **Docker** - Pre-installed with NVIDIA Container Toolkit
- **Podman** - Rootless containers
- **NVIDIA Container Toolkit** - GPU passthrough to containers

### LLM Development
- **Ollama** - Run local LLMs easily
- **llama.cpp** - Efficient CPU/GPU inference
- **vLLM** - High-throughput LLM serving
- **Text Generation WebUI** - Local LLM chat interface

## System Requirements

| Component | Minimum | Recommended | Heavy Training |
|-----------|---------|-------------|----------------|
| CPU | 8-core | 16-core | 32-core+ |
| RAM | 16 GB | 64 GB | 128 GB+ |
| GPU | RTX 3060 12GB | RTX 4090 24GB | Multi-GPU setup |
| GPU VRAM | 8 GB | 24 GB | 48 GB+ total |
| Storage | 256 GB NVMe | 1 TB NVMe | 2 TB+ NVMe RAID |

### Supported GPUs

#### NVIDIA (Recommended)
| Series | Cards | CUDA Compute |
|--------|-------|--------------|
| RTX 40 | 4090, 4080, 4070 Ti | 8.9 |
| RTX 30 | 3090, 3080, 3070 | 8.6 |
| RTX 20 | 2080 Ti, 2080, 2070 | 7.5 |
| Tesla/Datacenter | A100, V100, H100 | 8.0+ |

#### AMD (ROCm Support)
| Series | Cards |
|--------|-------|
| RX 7000 | 7900 XTX, 7900 XT |
| RX 6000 | 6900 XT, 6800 XT |
| Instinct | MI250X, MI210, MI100 |

## Installation

### Download
1. Download from [aegis-os.com/download/aidev](https://aegis-os.com/download/aidev)
2. Verify checksum:
   ```bash
   sha256sum aegis-os-aidev-3.0.0.iso
   ```

### Installation
```bash
# Flash to USB
sudo dd if=aegis-os-aidev-3.0.0.iso of=/dev/sdX bs=4M status=progress
```

Boot from USB and follow the installer. The AI Developer edition includes additional setup steps:
1. GPU driver selection (NVIDIA/AMD)
2. CUDA version selection
3. Initial framework installation
4. JupyterLab configuration

## Included Aegis Tools

### ML Studio (`aegis-ml-studio`)
Unified ML development interface:
- Project management
- Environment creation
- Training job monitoring
- Model registry
- Experiment tracking (MLflow integration)

### Compute Stack (`aegis-compute-stack`)
GPU and compute management:
- GPU utilization monitoring
- Memory management
- Multi-GPU job scheduling
- Temperature and power monitoring
- Automatic throttling prevention

### Model Hub (`aegis-model-hub`)
Local model management:
- Download from Hugging Face
- GGUF/GGML model support
- Quantization tools
- Model benchmarking
- Storage optimization

### Inference Engine (`aegis-inference-engine`)
Deploy models locally:
- REST API generation
- Batch inference
- Streaming responses
- Load balancing
- Model hot-swapping

### GPU Tools (`aegis-gpu-tools`)
Low-level GPU management:
- Driver updates
- CUDA toolkit management
- cuDNN installation
- TensorRT optimization
- Power profile management

### Data Science Tools (`aegis-data-science`)
Data preparation utilities:
- Dataset browser
- Data cleaning tools
- Feature engineering
- Visualization dashboards
- Database connectors

### LLM Tools (`aegis-llm-tools`)
Local LLM development:
- Ollama integration
- llama.cpp management
- Prompt engineering workspace
- RAG pipeline builder
- Fine-tuning utilities

## Development Environment

### Python Environment
Aegis AI Developer uses virtual environments for clean dependency management:

```bash
# Create new ML environment
python -m venv ~/ml-env
source ~/ml-env/bin/activate

# Or use conda (included)
conda create -n myproject python=3.11
conda activate myproject
```

### Pre-configured Aliases
```bash
# ~/.bashrc additions
alias jl='jupyter lab'
alias tb='tensorboard --logdir'
alias gpu='nvidia-smi'
alias gpuwatch='watch -n 1 nvidia-smi'
alias trainenv='source ~/ml-env/bin/activate'
```

### JupyterLab Setup
JupyterLab is pre-configured with:
- GPU memory extension
- Variable inspector
- Git integration
- Collaborative editing
- Custom AI themes

Start JupyterLab:
```bash
jupyter lab --no-browser --port=8888
```

### Docker with GPU
```bash
# Run PyTorch container with GPU
docker run --gpus all -it pytorch/pytorch:latest

# Run TensorFlow with GPU
docker run --gpus all -it tensorflow/tensorflow:latest-gpu

# Custom container with all GPUs
docker run --gpus all \
  -v /data:/data \
  -v $(pwd):/workspace \
  -p 8888:8888 \
  aegis-ml-base:latest
```

## Quick Start Guides

### Training Your First Model

```python
# train_mnist.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# Check GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load data
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_data = datasets.MNIST('./data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_data, batch_size=64, shuffle=True)

# Simple model
model = nn.Sequential(
    nn.Flatten(),
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
).to(device)

# Train
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()

for epoch in range(5):
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} complete")

# Save model
torch.save(model.state_dict(), "mnist_model.pth")
```

### Running Local LLMs

```bash
# Start Ollama
ollama serve &

# Pull a model
ollama pull llama2:7b

# Run inference
ollama run llama2:7b "Explain neural networks simply"

# Or use the API
curl http://localhost:11434/api/generate -d '{
  "model": "llama2:7b",
  "prompt": "Hello, how are you?"
}'
```

### Fine-tuning with Hugging Face

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset

# Load model and tokenizer
model_name = "meta-llama/Llama-2-7b-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

# Load dataset
dataset = load_dataset("your_dataset")

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    fp16=True,
    save_steps=100,
    logging_steps=10,
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
)
trainer.train()
```

## Monitoring & Optimization

### GPU Monitoring
```bash
# Real-time GPU stats
nvidia-smi dmon

# Detailed GPU info
nvidia-smi -q

# GPU memory by process
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
```

### Training Monitoring
```bash
# Start TensorBoard
tensorboard --logdir=./runs --port=6006

# MLflow tracking
mlflow ui --port=5000
```

### Memory Optimization
```python
# Enable gradient checkpointing
model.gradient_checkpointing_enable()

# Use mixed precision
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    output = model(input)
    loss = criterion(output, target)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

## Pricing & Licensing

**Price: $89 (one-time)**

Includes:
- Lifetime license for AI Developer Edition
- All future 3.x updates
- Priority beta access
- Priority support (1 year)

### Upgrade Paths
| From | To | Price |
|------|-----|-------|
| Freemium | AI Developer | $89 |
| AI Developer | Gamer+AI | $40 |
| Basic | AI Developer | $49 |

## Support

### Documentation
- [docs.aegis-os.com/aidev](https://docs.aegis-os.com/aidev)
- [Wiki: ML Optimization Guides](https://wiki.aegis-os.com/ml)

### Community
- [Discord #ai-dev](https://discord.gg/aegis-os)
- [Reddit r/AegisAI](https://reddit.com/r/aegisai)

### Troubleshooting

#### CUDA not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA version
nvcc --version

# Reinstall CUDA
sudo pacman -S cuda cudnn
```

#### Out of GPU memory
1. Reduce batch size
2. Enable gradient checkpointing
3. Use mixed precision (fp16/bf16)
4. Use DeepSpeed or FSDP for distributed training

#### Slow training
1. Check GPU utilization with `nvidia-smi`
2. Optimize data loading (num_workers, pin_memory)
3. Use compiled models (torch.compile)
4. Profile with PyTorch Profiler

## Contributing

### Development
```bash
git clone https://github.com/DeQuackDealer/AegisOSRepo.git
cd AegisOSRepo
git checkout preview/aidev
```

### Contributing ML Tools
- Share optimized training scripts
- Contribute model configs
- Report framework compatibility issues
- Improve documentation

See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 3.0.0 | 2024-12 | Arch Linux base, CUDA 12.x |
| 2.5.0 | Legacy | Ubuntu-based (deprecated) |

---

**Aegis OS AI Developer** - Your ML workstation, ready to go.
