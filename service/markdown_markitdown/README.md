# Markitdown Converter Service

This service provides PDF to Markdown conversion using Microsoft's [markitdown](https://github.com/microsoft/markitdown) library.

## Features

- Convert single PDF files to Markdown
- Batch convert all PDF files in a directory
- Support for subdirectory processing
- Preserve directory structure in output
- Comprehensive error handling and logging
- Conversion statistics

## Installation

The required dependencies are already included in the project's `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from service.markdown.markitdown_converter import MarkitdownConverter

# Initialize converter
converter = MarkitdownConverter()

# Convert all PDFs in old_version directory
results = converter.convert_old_version_docs()
print(f"Converted {len(results)} files")
```

### Convert Single File

```python
# Convert a specific PDF file
result = converter.convert_pdf_to_markdown("raw_docs/old_version/example.pdf")
print(f"Converted to: {result}")
```

### Convert with Custom Directories

```python
# Use custom input and output directories
converter = MarkitdownConverter(
    input_dir="custom_input",
    output_dir="custom_output"
)

results = converter.convert_directory()
```

### Convert Specific Subdirectory

```python
# Convert PDFs in a specific subdirectory
results = converter.convert_directory("old_version/dm")
```

### Get Conversion Statistics

```python
stats = converter.get_conversion_stats()
print(f"Input PDFs: {stats['input_pdfs_count']}")
print(f"Output MDs: {stats['output_mds_count']}")
```

## Command Line Usage

You can also use the converter from the command line:

```bash
# Convert all PDFs in old_version directory
python -m service.markdown.markitdown_converter

# Convert specific file
python -m service.markdown.markitdown_converter --file "raw_docs/old_version/example.pdf"

# Convert with custom directories
python -m service.markdown.markitdown_converter --input-dir "custom_input" --output-dir "custom_output"

# Convert specific subdirectory
python -m service.markdown.markitdown_converter --subdir "old_version/dm"
```

## Directory Structure

```
service/markdown/
├── __init__.py
├── markitdown_converter.py    # Main converter class
├── test_markitdown_converter.py  # Test cases
├── example_usage.py           # Usage examples
└── README.md                  # This file
```

## Output

Converted markdown files are saved to `markdown/converted/` by default, preserving the original directory structure from the input.

For example:
- `raw_docs/old_version/example.pdf` → `markdown/converted/old_version/example.md`
- `raw_docs/old_version/dm/file.pdf` → `markdown/converted/old_version/dm/file.md`

## Error Handling

The converter includes comprehensive error handling:

- File not found errors
- Invalid file type errors (non-PDF files)
- Conversion errors with detailed logging
- Graceful handling of batch conversion failures

## Testing

Run the test suite:

```bash
python -m pytest service/markdown/test_markitdown_converter.py -v
```

## Examples

See `example_usage.py` for detailed usage examples.

## Dependencies

- `markitdown[all]>=0.0.1a0` - Microsoft's markitdown library
- `pathlib` - Path manipulation (built-in)
- `logging` - Logging (built-in)
