# Mistral Document Processor

## Overview
Mistral Document Processor is a Python-based tool that combines OCR processing and requirement extraction using Mistral AI. It enables users to extract text from PDFs, convert it into markdown format, and extract structured requirements from documents.

## Features
- **OCR Processing:**
  - Extracts text from PDF documents using Mistral AI OCR.
  - Converts extracted text into markdown format with embedded images.
  - Saves OCR results as JSON and markdown files.

- **Requirement Extraction:**
  - Reads input text files containing structured requirements.
  - Uses Mistral AI to extract and structure requirement data.
  - Saves the extracted requirements in CSV format.

## Why Use This Project?
- Automates text extraction from scanned PDFs.
- Provides well-structured markdown output for easy readability.
- Extracts requirements from structured documents into CSV format.
- Facilitates analysis and storage of structured technical requirements.

## Installation
### Prerequisites
- Python 3.8+
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- Set up an environment variable for `MISTRALAI_API_KEY`.

## Usage
### **OCR Processing**
```sh
python mistral_ocr.py <PDF_PATH>
```
#### **Expected Output**
- A `.json` file containing raw OCR results.
- A `.md` file with extracted markdown-formatted text and images.
- The extracted markdown is also displayed in the terminal.

### **Requirement Extraction**
```sh
python requirement_extractor.py
```
#### **Expected Output**
- Extracted requirements saved in `output/requirements.csv`.
- Log messages indicating processing status.

## Configuration
- Modify `input_file` in `requirement_extractor.py` to process a different document.
- Update `mistral_ocr.py` settings for image resizing and format adjustments.
- Modify the prompt in `get_mistral_response()` to refine requirement extraction.

## Logging and Debugging
- Logs are displayed in the console with timestamps and error details.

## License
This project is licensed under the MIT License.

## Contributing
Feel free to submit issues or pull requests to enhance the functionality.

