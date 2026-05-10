# GEMINI.md

# Codename: Count Spatula

## Project Overview

This project, "count-spatula," is a Python-based tool for generating 3D models of Gridfinity-compatible bins. It utilizes the `build123d` and `gridfinity-build123d` libraries to create custom-sized bins and compartments, and then exports them as STL files suitable for 3D printing.

Initially proof-of-concept code is being created in Jupyter notebooks. When I'm satisfied with the code it will be converted into a python module and eventually published.

The module will include code to generate assorted bins for storing cutlery and kitchenware, based on the Gridfinity organiser template. The bins will be generated parametrically, so users can enter a simple command and get an STL file as output.

## Collaboration Guidelines

When providing technical assistance:

- **Be objective and critical**: Focus on technical correctness over agreeability
- **Challenge assumptions**: If code has clear technical flaws, point them out directly
- **Prioritize correctness**: Don't compromise on proper implementation to avoid disagreement
- **Think through implications**: Consider how users will actually use features in practice
- **Be direct about problems**: If something is wrong or will cause user confusion, say so clearly

The goal is to build robust, well-designed software, not to avoid technical disagreements.

## Programming Guidelines

- Comments should be proper sentences, with correct grammar and punctuation,
  including the use of capitalization and periods.
  - EXCEPT for comments that are simply single words or short phrases
    such as `// TODO: ...` or `// Deprecated` or bullet-points.
- Where defensive checks are added, include a comment explaining why they are
  appropriate (not necessary, since defensive checks are not necessary).

## Programming Style Guidelines

For projects we own, including this one, we adopt the following single, uniform, good practice for our own projects and work entirely cross-platform with no use of "smart" defaults (e.g. Git's autocrlf).

- I prefer LF to CRLF/CR line endings in source code files and documentation files.
- I prefer text files to use new-line (LF) as a terminator rather than a separator
  i.e. newlines at the end of non-empty files, including on Windows.
- And lines should not have trailing whitespace EXCEPT in Markdown files where
  trailing whitespace indicates a line break. In those cases, use a single space
  at the end of the line to indicate a line break.
- We use 120 as the maximum line-length and not 80 characters. The detailed guideline
  is that the length first-to-last non-whitespace character should be 80 characters
  and that an additional 40 characters of indentation is allowed.
- Indentation in source files should use spaces only, no tabs EXCEPT in Golang or 
  Makefiles where tabs are effectively required.
- Use 4 spaces per indentation level EXCEPT when working in YAML/JSON files where 2 spaces per indentation level is more practical owning to higher nesting levels.
- UTF-8 encoding should be used for all text files EXCEPT when working with compilers/interpreters that do not support UTF-8.

## Developer documentation guidelines

- Use Unix-style paths (forward slashes) in code and documentation, even on Windows.
- Use Markdown for documentation files wherever possible with the .md file extension.

## Building and Running

### Dependencies

This project uses `uv` to manage Python dependencies. The required packages are listed in `pyproject.toml`.

**Production Dependencies:**
- `gridfinity-build123d` (sourced directly from a GitHub repository)

**Development Dependencies:**
- `jupyter`
- `ocp-vscode`
- `ruff`

### Installation

To install the necessary dependencies, you will need `uv` installed. Then, run the following command in your terminal:

```bash
uv pip install -e .[dev]
```

### Running the aplication

To generate the STL file, run the `main.py` script:

```bash
python main.py
```

This will create a file named `chopping_blocks_6x4.stl` in the root directory.

## Development Conventions

### Linting

This project uses `ruff` for code linting and formatting. To check the code for issues, run:

```bash
ruff check .
```

To automatically fix issues, run:
```bash
ruff check . --fix
```

### 3D Model Viewing

The inclusion of `ocp-vscode` suggests that the recommended development environment includes Visual Studio Code with the OCP CAD viewer extension. This allows for interactive viewing of the generated 3D models directly within the editor. The `show_all()` call in `main.py` will display the model in the OCP viewer.
