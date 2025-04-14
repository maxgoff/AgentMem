# Interactive AgentMem Tutorials

This directory contains interactive Jupyter notebook tutorials for the AgentMem package. These notebooks allow you to learn about AgentMem's features through hands-on examples.

## Available Notebooks

- [**AgentMem Interactive Tutorial**](agentmem_interactive_tutorial.ipynb): A comprehensive tutorial covering all memory types and key features of AgentMem.

## Running the Notebooks

### Prerequisites

- Python 3.8 or later
- Jupyter Notebook or JupyterLab
- AgentMem with vector search capabilities installed

### Installation

1. Install Jupyter if you don't have it already:
   ```bash
   pip install notebook
   ```

2. Install AgentMem with vector search capabilities:
   ```bash
   pip install "agentmem[vector]"
   ```

### Running the Tutorials

1. Start Jupyter:
   ```bash
   jupyter notebook
   ```

2. Navigate to this directory and open the desired notebook.

3. Run the cells one by one to see the results.

## Tutorial Contents

The main tutorial notebook covers:

1. Creating memory instances of different types
2. Working with semantic memory
3. Working with episodic memory
4. Working with procedural memory
5. Memory persistence and management
6. Building an agent with integrated memory types
7. Advanced features like concurrency and metrics

## Notes

- The tutorials create temporary files in directories named `notebook_memory` and `agent_memory`. You can clean these up at the end of the tutorial.
- Vector search requires additional dependencies (sentence-transformers and chromadb) which should be installed automatically when you install AgentMem with the `[vector]` extra.
- Some cells may take a while to run when using vector search for the first time, as the embedding models need to be downloaded.

## Troubleshooting

If you encounter issues:

- Make sure you have the latest version of AgentMem installed
- Ensure all dependencies are installed correctly
- Try running the notebook with a fresh kernel
- Check the [troubleshooting guide](../../troubleshooting.md) for common issues

For more help, please open an issue on the [GitHub repository](https://github.com/maxgoff/memory).