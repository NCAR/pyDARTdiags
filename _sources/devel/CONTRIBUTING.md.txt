# Contributors Guide

## Introduction

Welcome to the pyDARTdiags contributors guide! We appreciate your interest in contributing to the project. 
Whether you're fixing bugs, adding new features, improving documentation, or writing tests, please follow
the contributors guide.

## What Can I Do?

There are many ways you can contribute to pyDARTdiags:
- **Report Bugs**: If you find a bug, please report it by opening an [issue](https://github.com/NCAR/pyDARTdiags/issues).
- **Fix Bugs**: Look through the [issue tracker](https://github.com/NCAR/pyDARTdiags/issues) for bugs that need fixing.
- **Add Features**: If you have an idea for a new feature, open an issue to discuss it before starting work.
- **Improve Documentation**: Help us improve our documentation by making it clearer and more comprehensive.
- **Write Tests**: We use the [pytest framework](https://docs.pytest.org/en/stable/).

## Reporting a Bug

If you find a bug, please report it by opening an issue on our [GitHub repository](https://github.com/NCAR/pyDARTdiags/issues). 
Include as much detail as necessary to help us understand and reproduce the issue.

A bug report should contain the following:

* The steps someone needs to take to reproduce the bug.
* What you expected to happen.
* What actually happened.

## Setting up your development environment

For developers of pyDARTdiags, we recommend installing pyDARTdiags as a local project in “editable” mode.

To set up your development environment, follow these steps:

1. **Create a Virtual Environment**:
    ```sh
    python -m venv 
    source py-dart/bin/activate 
    ```

2. **Clone the Repository**:
    ```sh
    git clone https://github.com/NCAR/pyDARTdiags.git
    cd pyDARTdiags
    ```

3. **Install Dependencies**:
    ```sh
    pip install -r docs/requirements.txt
    ```

4. **Install the Package in Editable Mode**:
    ```sh
    pip install -e .
    ```

pyDARTdiags is now installed in your virtual enviroment in editable mode.

## Pull Requests

We welcome pull requests! To submit a pull request:

1. **Fork the Repository**: Click the "Fork" button on the repository's GitHub page.
2. **Create a Branch**: Create a new branch for your work.
    ```sh
    git checkout -b my-feature-branch
    ```
3. **Make Changes**: Make your changes and commit them. 
4. **Push to Your Fork**: Push your changes to your forked repository.
    ```sh
    git push origin my-feature-branch
    ```
5. **Open a Pull Request**: Open a pull request from your forked repository to the main repository. Provide a 
description of your changes - the "why" - and note any issues that are being addressed. 

## Source Code

The source code for pyDARTdiags is available on our [GitHub repository](https://github.com/NCAR/pyDARTdiags). Feel free to explore and understand the codebase.

## Documentation

The documentation is built using Sphinx, is written in rst or MyST, and can be found in the docs
directory.
The API guide is built directly from docstrings in the python code, using Sphinx autodoc.
You can contribute by improving existing documentation or adding examples. 

Assuming you have set up your development environment as above, with the dependencies listed
in docs/requirements.txt, you can build the documentation locally

1. **Navigate to the docs directory**:
    ```sh
    cd docs
    ```

2. **Build the Documentation**:
    ```sh
    make html
    ```

## Tests

We use `pytest` for testing.

### Running Tests

To run the tests, use the following command:

```sh
cd tests
pytest
```

Or for more verbose output:

```sh
pytest -v
```

Make sure all tests pass before submitting a pull request.

### Code Coverage

We use [Codecov](https://about.codecov.io/) to measure the percentage of code covered by tests. 
You can view the code coverage reports for the project at [Codecov for pyDARTdiags](https://app.codecov.io/gh/NCAR/pyDARTdiags).