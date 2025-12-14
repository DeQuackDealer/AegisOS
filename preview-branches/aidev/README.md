# Aegis OS - AI Developer Tools

This branch contains AI/ML development tools for Aegis OS AI Developer Edition.

## What's Included

### ML Development
| Tool | Description |
|------|-------------|
| `aegis-ml-studio` | Integrated ML development environment |
| `aegis-model-hub` | Model management and versioning |
| `aegis-inference-engine` | Local model inference server |

### GPU Management
| Tool | Description |
|------|-------------|
| `aegis-gpu-tools` | GPU monitoring and management |
| `aegis-compute-stack` | CUDA/ROCm stack management |

### Data Science
| Tool | Description |
|------|-------------|
| `aegis-data-science` | Data science toolkit launcher |
| `aegis-llm-tools` | LLM interaction and fine-tuning |

## For Contributors

### Getting Started

1. Clone this branch:
   ```bash
   git clone -b preview/aidev https://github.com/DeQuackDealer/AegisOSRepo.git aegis-aidev
   cd aegis-aidev
   ```

2. Dependencies:
   - Python 3.10+
   - CUDA 12.x or ROCm
   - PyTorch, TensorFlow (optional)
   - Docker/Podman

### Testing

```bash
# Test GPU detection
python3 usr/local/bin/aegis-gpu-tools --check

# Validate Python syntax
find usr -name "*.py" -exec python3 -m py_compile {} \;
```

### Key Features to Work On

- [ ] Add support for more ML frameworks
- [ ] Improve model quantization tools
- [ ] Better GPU memory management
- [ ] Integration with Hugging Face Hub
- [ ] Ollama integration improvements

### Code Guidelines

- Support both NVIDIA (CUDA) and AMD (ROCm)
- Graceful fallback to CPU when no GPU
- Use environment variables for configuration
- Include progress bars for long operations

### Submitting Changes

1. Fork the repository
2. Create a feature branch from `preview/aidev`
3. Test on both NVIDIA and AMD if possible
4. Document any new dependencies
5. Submit a Pull Request

## File Structure

```
usr/
  local/
    bin/           # AI/ML tools
  share/
    applications/  # .desktop files
etc/
  aegis/           # Model configs, GPU settings
  systemd/         # Background services
```

## Environment Variables

```bash
AEGIS_CUDA_PATH=/opt/cuda
AEGIS_MODEL_CACHE=~/.cache/aegis/models
AEGIS_DEFAULT_DEVICE=cuda  # or rocm, cpu
```

## Supported Backends

- **CUDA**: NVIDIA GPUs (GTX 10xx+)
- **ROCm**: AMD GPUs (RX 5000+)
- **CPU**: Fallback for all systems
- **Ollama**: Local LLM inference
- **ONNX Runtime**: Cross-platform inference

## Questions?

Open an issue: https://github.com/DeQuackDealer/AegisOS/issues

## License

See the main repository for license information.
