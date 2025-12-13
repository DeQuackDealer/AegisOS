# Aegis OS AI Developer Tools (preview/aidev)

## What This Branch Contains

This branch contains **ONLY the AI/ML-specific tools and configurations** that are layered on top of the base OS to create the AI Developer Edition. If you want to improve machine learning workflows, GPU compute, or AI tooling on Aegis OS, this is where you contribute.

## Included AI Tools

### ML Development
```
usr/local/bin/
├── aegis-ml-studio            # Unified ML development interface
│                              # - Project management
│                              # - Environment creation
│                              # - Experiment tracking (MLflow)
│                              # - Model registry
│
├── aegis-model-hub            # Local model management
│                              # - Download from Hugging Face
│                              # - GGUF/GGML support
│                              # - Quantization tools
│                              # - Model benchmarking
│
├── aegis-training-optimizer   # Training optimization utilities
│                              # - Mixed precision setup
│                              # - Gradient checkpointing
│                              # - Distributed training config
│
└── aegis-dataset-manager      # Dataset management
                               # - Download popular datasets
                               # - Data versioning
                               # - Preprocessing pipelines
```

### GPU & Compute
```
usr/local/bin/
├── aegis-compute-stack        # GPU compute management
│                              # - CUDA toolkit management
│                              # - cuDNN installation
│                              # - TensorRT optimization
│                              # - Multi-GPU configuration
│
├── aegis-gpu-tools            # Low-level GPU utilities
│                              # - Driver updates
│                              # - Power profiles
│                              # - Temperature monitoring
│                              # - Memory management
│
└── aegis-ai-monitor           # Training job monitoring
                               # - GPU utilization graphs
                               # - Memory tracking
                               # - Training loss curves
                               # - ETA estimation
```

### Inference & Deployment
```
usr/local/bin/
├── aegis-inference-engine     # Model deployment
│                              # - REST API generation
│                              # - Batch inference
│                              # - Streaming responses
│                              # - Load balancing
│
├── aegis-llm-tools            # Large Language Model utilities
│                              # - Ollama integration
│                              # - llama.cpp management
│                              # - Prompt engineering
│                              # - RAG pipeline builder
│
└── aegis-data-science         # Data science utilities
                               # - Jupyter integration
                               # - Visualization tools
                               # - Statistical analysis
                               # - Database connectors
```

## System Configurations

### CUDA Environment
```
etc/profile.d/
└── aegis-cuda-env.sh          # CUDA paths and environment
```

### GPU Optimization
```
etc/modprobe.d/
└── aegis-nvidia.conf          # NVIDIA module parameters
```

### Container Support
```
etc/docker/daemon.json         # Docker with NVIDIA runtime
etc/nvidia-container-runtime/  # NVIDIA container toolkit config
```

### Systemd Services
```
etc/systemd/system/
├── aegis-gpu-monitor.service      # GPU monitoring daemon
├── aegis-jupyter.service          # JupyterLab service
└── aegis-inference-engine.service # Model serving daemon
```

### Edition Configuration
```
etc/aegis/
├── tier.json                  # AI Developer tier definition
├── aidev-packages.list        # AI-specific packages
├── cuda-config.json           # CUDA toolkit settings
├── ml-frameworks.json         # Framework versions
└── model-cache.json           # Model storage settings
```

## What You Can Contribute

### Priority Areas

1. **ML Studio Improvements**
   - Better experiment tracking
   - Hyperparameter optimization UI
   - AutoML integration
   - Weights & Biases support

2. **Model Hub Features**
   - More model format support
   - Better quantization options
   - Model comparison tools
   - Fine-tuning wizards

3. **GPU Tools**
   - AMD ROCm support
   - Better multi-GPU handling
   - Cloud GPU integration
   - Power efficiency profiles

4. **LLM Tooling**
   - Better Ollama integration
   - More inference backends
   - RAG improvements
   - Agent frameworks

5. **Data Science**
   - More database connectors
   - Better visualization
   - Automated EDA tools
   - Feature engineering helpers

### How to Contribute

1. Fork and clone the repository
2. Switch to this branch:
   ```bash
   git checkout preview/aidev
   ```
3. Make your changes to the AI tools
4. Test with real ML workloads
5. Submit a pull request to `preview/aidev`

### Testing Your Changes

```bash
# Test ML Studio
python3 usr/local/bin/aegis-ml-studio --test

# Test GPU tools (requires NVIDIA GPU)
python3 usr/local/bin/aegis-gpu-tools --diagnose

# Test inference engine
python3 usr/local/bin/aegis-inference-engine --test-api

# Validate all Python scripts
for f in usr/local/bin/aegis-*; do
  python3 -m py_compile "$f" && echo "OK: $f"
done

# Test with PyTorch
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Files NOT in This Branch

This branch does NOT contain:
- Base OS tools (those are in `preview/base-os`)
- Gaming tools (those are in `preview/gamer`)
- Website code
- Build system
- Other editions (workplace, server, basic, gamer-ai)

## Syncing with Main

AI tools here are merged into `main` when ready:
```bash
# Maintainers merge approved changes to main
git checkout main
git merge preview/aidev --no-ff -m "Merge AI development improvements"
```

## AI Developer Edition Packages

Additional packages installed with AI Developer Edition:

### Python & ML
- `python`, `python-pip`, `python-virtualenv`
- `python-numpy`, `python-pandas`, `python-matplotlib`
- `python-scikit-learn`
- `jupyterlab`

### Deep Learning (installed via pip)
- PyTorch with CUDA
- TensorFlow with GPU support
- JAX
- Hugging Face Transformers
- ONNX Runtime

### CUDA Stack (NVIDIA systems)
- `cuda`, `cudnn`
- NVIDIA Container Toolkit

### Containers
- `docker`, `docker-compose`
- `podman`

### Development
- `git`, `git-lfs`
- `tmux`, `htop`
- VS Code (via AUR)

### LLM Tools (installed via pip/binary)
- Ollama
- llama.cpp
- vLLM

## Recommended GPU Hardware

| GPU | VRAM | Best For |
|-----|------|----------|
| RTX 4090 | 24GB | Large models, fast training |
| RTX 3090 | 24GB | Good balance of price/performance |
| RTX 4080 | 16GB | Medium models |
| A100 | 40/80GB | Enterprise, huge models |
| H100 | 80GB | State-of-the-art performance |

## Questions?

- Open an issue with the `aidev` label
- Join [Discord #ai-development](https://discord.gg/aegis-os)
- Check [Hugging Face](https://huggingface.co/) for model compatibility
