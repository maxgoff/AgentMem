# Installation Guide

This guide will help you install AgentMem and its dependencies.

## Prerequisites

AgentMem requires:

- Python 3.8 or higher
- pip (Python package installer)

## Basic Installation

The simplest way to install AgentMem is via pip:

```bash
pip install agentmem
```

This will install AgentMem with its basic dependencies.

## Development Installation

If you want to contribute to AgentMem or use the latest development version, you can install it from source:

```bash
git clone https://github.com/maxgoff/memory.git
cd memory/agentmem
pip install -e .
```

The `-e` flag installs the package in "editable" mode, meaning changes to the source code will be immediately available without reinstalling.

## Installing with Vector Search Support

For vector search capabilities, you need additional dependencies:

```bash
pip install "agentmem[vector]"
```

This will install additional packages like `sentence-transformers` and `chromadb` that are required for vector-based semantic search.

## Version Compatibility

### Python Versions

AgentMem is compatible with Python 3.8 through 3.12.

### NumPy Compatibility

AgentMem works with both NumPy 1.x and 2.x:

- With **NumPy 2.x**: You may see warnings related to the sentence-transformers package, but these are non-fatal and automatically suppressed during import.
- For a completely warning-free experience: You can downgrade NumPy with `pip install "numpy<2"`.

### Dependencies

Here are the key dependencies and their compatible versions:

| Dependency | Minimum Version | Notes |
|------------|----------------|-------|
| pydantic | 2.0.0 | For data validation |
| numpy | 1.20.0 | For numerical operations |
| sentence-transformers | 2.2.2 | For vector embeddings (optional) |
| chromadb | 0.4.0 | For vector database storage (optional) |
| psutil | 5.9.0 | For system monitoring |
| joblib | 1.2.0 | For parallel processing |

## Troubleshooting

### Common Installation Issues

#### Vector Search Import Errors

If you see errors like:

```
ImportError: cannot import name 'VectorStorage' from 'agentmem.storage'
```

Make sure you've installed the vector search dependencies:

```bash
pip install "sentence-transformers>=2.2.2" "chromadb>=0.4.0"
```

#### NumPy Warnings

If you see warnings about NumPy compatibility:

```
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.4...
```

These warnings are non-fatal and are automatically suppressed during normal operation. They indicate that some packages (like sentence-transformers) were compiled with NumPy 1.x but are running with NumPy 2.x.

Options:
1. Ignore the warnings (they don't affect functionality)
2. Downgrade NumPy: `pip install "numpy<2"`

### Getting Help

If you encounter issues not covered here, please:

1. Check the [GitHub issues](https://github.com/maxgoff/memory/issues) to see if your problem has been reported
2. Open a new issue if needed