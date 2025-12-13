# Aegis OS AI Developer Edition

**Your complete AI/ML development workstation - GPU-accelerated, container-ready**

[![License](https://img.shields.io/badge/License-Open%20Source-green.svg)]()
[![Arch Linux](https://img.shields.io/badge/Based%20on-Arch%20Linux-1793D1.svg)]()
[![CUDA](https://img.shields.io/badge/CUDA-Ready-76B900.svg)]()
[![PyTorch](https://img.shields.io/badge/PyTorch-Included-EE4C2C.svg)]()

---

## Overview

Aegis OS AI Developer Edition is designed for machine learning engineers, data scientists, and AI researchers. It comes pre-configured with CUDA, cuDNN, PyTorch, TensorFlow, JupyterLab, and containerized workflows for reproducible research.

**This is an open-source preview** - Join us in building the ultimate ML workstation!

---

## Features

### GPU Compute
- **CUDA Toolkit** (latest)
- **cuDNN** for deep learning
- **ROCm** support for AMD GPUs
- **OpenCL** for cross-platform compute
- GPU monitoring and management tools

### ML Frameworks
- **PyTorch** with CUDA support
- **TensorFlow** with GPU acceleration
- **JAX** for high-performance computing
- **scikit-learn** for classical ML
- **XGBoost/LightGBM** for gradient boosting

### Development Environment
- **JupyterLab** with extensions
- **VS Code** with Python/ML extensions
- **Neovim** with LSP support
- **Conda/Mamba** package manager
- **Poetry** for dependency management

### Containers & MLOps
- **Docker** with NVIDIA Container Toolkit
- **Podman** rootless containers
- **Kubernetes** CLI tools
- **MLflow** for experiment tracking
- **DVC** for data versioning

### Data Science Tools
- **Pandas, NumPy, SciPy**
- **Matplotlib, Seaborn, Plotly**
- **Apache Spark** (PySpark)
- **Dask** for parallel computing
- **Polars** for fast dataframes

### LLM & Generative AI
- **Ollama** for local LLMs
- **llama.cpp** for efficient inference
- **Hugging Face Transformers**
- **LangChain** for LLM apps
- **ONNX Runtime** for model deployment

---

## Package List

### NVIDIA Stack
```
nvidia
nvidia-utils
lib32-nvidia-utils
cuda
cuda-tools
cudnn
nvidia-container-toolkit
```

### AMD ROCm (Alternative)
```
rocm-core
rocm-hip-runtime
rocm-opencl-runtime
```

### Python ML
```
python
python-pip
python-virtualenv
python-pytorch-cuda
python-torchvision-cuda
python-tensorflow-cuda
python-numpy
python-pandas
python-matplotlib
python-scikit-learn
python-jupyterlab
```

### Containers
```
docker
docker-compose
podman
kubectl
helm
```

### Development
```
visual-studio-code-bin (AUR)
neovim
git
git-lfs
tmux
```

### MLOps
```
mlflow
dvc
tensorboard
```

See `build-system/archiso/packages/aidev.txt` for the complete list.

---

## Building from Source

### Prerequisites
- Arch Linux system with NVIDIA GPU
- Root access
- 20GB+ free disk space
- archiso package

### Build Steps

```bash
# Clone the repository
git clone https://github.com/DeQuackDealer/AegisOSRepo.git
cd AegisOSRepo

# Checkout the AI dev preview branch
git checkout preview/aidev

# Install archiso
sudo pacman -S archiso

# Build the ISO
cd build-system
sudo python build-aegis.py --edition aidev --real-build
```

---

## Directory Structure

```
AegisOSRepo/
├── build-system/
│   ├── archiso/
│   │   ├── packages/
│   │   │   └── aidev.txt         # AI/ML package list
│   │   └── airootfs/
│   │       └── etc/
│   │           └── conda/        # Conda config
│   ├── overlays/
│   │   └── aidev/
│   │       ├── jupyter/          # JupyterLab config
│   │       └── vscode/           # VS Code settings
│   └── build-aegis.py
├── docs/
│   └── editions/
│       └── aidev/
│           └── README.md         # This file
└── CONTRIBUTING.md
```

---

## GPU Setup

### NVIDIA GPUs

Verify CUDA installation:
```bash
nvidia-smi
nvcc --version
python -c "import torch; print(torch.cuda.is_available())"
```

### AMD GPUs (ROCm)

Verify ROCm installation:
```bash
rocminfo
python -c "import torch; print(torch.cuda.is_available())"  # Uses HIP
```

### Multi-GPU Training

Set visible devices:
```bash
export CUDA_VISIBLE_DEVICES=0,1  # Use GPUs 0 and 1
```

---

## Development Workflows

### JupyterLab

Start JupyterLab:
```bash
jupyter lab --no-browser --port=8888
```

Pre-installed extensions:
- jupyterlab-git
- jupyterlab-lsp
- jupyterlab-tensorboard

### VS Code

Pre-installed extensions:
- Python
- Pylance
- Jupyter
- Docker
- Remote - SSH

### Conda Environments

Create ML environment:
```bash
conda create -n ml python=3.11 pytorch torchvision cuda-toolkit -c pytorch -c nvidia
conda activate ml
```

---

## Container Workflows

### Docker with GPU

```bash
# Run PyTorch container
docker run --gpus all -it pytorch/pytorch:latest

# Run TensorFlow container
docker run --gpus all -it tensorflow/tensorflow:latest-gpu

# Run custom training
docker run --gpus all -v $(pwd):/workspace my-training-image
```

### Podman (Rootless)

```bash
# Same syntax, no root needed
podman run --device nvidia.com/gpu=all -it pytorch/pytorch:latest
```

---

## Local LLMs

### Ollama

```bash
# Install and run Llama 2
ollama run llama2

# Run Code Llama
ollama run codellama

# API access
curl http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"Hello"}'
```

### llama.cpp

```bash
# Quantized inference
./main -m models/llama-7b.gguf -p "Write a poem about Linux"
```

---

## Customization

### Adding ML Packages

1. Edit `build-system/archiso/packages/aidev.txt`
2. For Python packages, add to pip requirements
3. For system packages, use pacman names
4. Test GPU compatibility
5. Submit a Pull Request

### JupyterLab Extensions

1. Add to `build-system/overlays/aidev/jupyter/`
2. Create install script
3. Document the extension
4. Submit a Pull Request

### Custom CUDA Libraries

1. Add to overlay directory
2. Update LD_LIBRARY_PATH in profile
3. Test with sample code
4. Submit a Pull Request

---

## Contributing

Help us build the best ML workstation! See [CONTRIBUTING.md](/CONTRIBUTING.md).

### Priority Contributions
- GPU driver compatibility
- ML framework updates
- Jupyter extensions
- MLOps tool integration
- Documentation and tutorials

### Testing

Test your changes:
1. Verify GPU detection
2. Run PyTorch CUDA test
3. Run TensorFlow GPU test
4. Test container GPU passthrough
5. Run a simple training job

---

## Benchmarks

Help us collect benchmarks! Submit results for:

| Model | GPU | Time | Notes |
|-------|-----|------|-------|
| ResNet-50 | - | - | Submit results |
| BERT | - | - | Submit results |
| Llama 7B | - | - | Submit results |

---

## Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| None yet | - | - |

---

## Roadmap

- [ ] Auto-detect and install GPU drivers
- [ ] Pre-built Conda environments
- [ ] Jupyter notebook templates
- [ ] Model zoo with pre-downloaded models
- [ ] Cloud GPU integration (vast.ai, Lambda)

---

## FAQ

**Q: Can I use multiple GPUs?**
A: Yes! Set `CUDA_VISIBLE_DEVICES` or use distributed training.

**Q: Does it support AMD GPUs?**
A: Yes, with ROCm. Select AMD packages during install.

**Q: How do I update CUDA?**
A: `sudo pacman -Syu cuda` - Arch keeps it current.

**Q: Can I train models overnight?**
A: Yes, use `tmux` or `screen` to keep sessions alive.

---

## Resources

- [PyTorch Docs](https://pytorch.org/docs/)
- [TensorFlow Docs](https://www.tensorflow.org/guide)
- [Hugging Face](https://huggingface.co/docs)
- [NVIDIA CUDA Docs](https://docs.nvidia.com/cuda/)

---

## Links

- [Main Repository](https://github.com/DeQuackDealer/AegisOSRepo)
- [Contributing Guide](/CONTRIBUTING.md)
- [Issue Tracker](https://github.com/DeQuackDealer/AegisOSRepo/issues)

---

**Build the future with Aegis OS AI Developer!**
