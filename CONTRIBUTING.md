# Contributing to AgentMem

Thank you for considering contributing to AgentMem! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate in all interactions related to this project. We aim to foster an inclusive and welcoming community.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report. Following these guidelines helps maintainers understand your report, reproduce the issue, and find related reports.

- **Use the GitHub issue tracker**: Submit bugs by creating a new issue using the bug report template.
- **Use a clear and descriptive title**
- **Provide a step-by-step reproduction**
- **Include your environment details**
- **Include relevant log outputs**

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion, including completely new features and minor improvements to existing functionality.

- **Use the GitHub issue tracker**: Submit enhancement requests by creating a new issue using the feature request template.
- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Include specific examples to demonstrate the steps**
- **Explain why this enhancement would be useful**

### Your First Code Contribution

Unsure where to begin contributing? Look for issues labeled:

- `good-first-issue`: issues which should only require a few lines of code and tests
- `help-wanted`: issues a bit more involved than `good-first-issue`
- `documentation`: issues related to improving documentation

### Pull Requests

Follow these steps to submit a pull request:

1. Fork the repository
2. Create a branch from `main`
3. Make your changes
4. Add or update tests as needed
5. Ensure all tests pass
6. Make sure your code follows the project's style guidelines
7. Submit a pull request

## Development Environment Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/yourusername/memory.git
   cd memory/agentmem
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   pip install pytest pytest-cov
   ```

4. Run tests:
   ```bash
   pytest tests/
   ```

## Coding Standards

- Follow [PEP 8](https://pep8.org/) style guidelines
- Document all functions, classes, and modules using docstrings
- Write tests for new features or bug fixes
- Use type hints for function and method arguments

## Commit Messages

- Use clear and descriptive commit messages
- Reference issue numbers in commit messages when applicable
- Keep commits focused on a single topic

## Testing

- Write unit tests for all new code
- Ensure all tests pass before submitting a pull request
- Aim for high test coverage

Thank you for contributing to AgentMem! Your efforts help make this project better for everyone.