from setuptools import setup, find_packages
import os

# Read the README file
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentmem",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "numpy>=1.20.0",
        "sentence-transformers>=2.2.2",
        "chromadb>=0.4.0",
        "joblib>=1.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
        ],
        "vector": [
            "sentence-transformers>=2.2.2",
            "chromadb>=0.4.0",
        ],
    },
    author="Max Goff",
    author_email="max.goff@example.com",
    description="A Python package for managing AI agent memory systems with persistence and vector search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maxgoff/memory",
    project_urls={
        "Documentation": "https://github.com/maxgoff/memory",
        "Bug Reports": "https://github.com/maxgoff/memory/issues",
        "Source Code": "https://github.com/maxgoff/memory",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
    ],
    keywords="ai, memory, agent, semantic, episodic, procedural, persistence, vector search",
    python_requires=">=3.8",
)