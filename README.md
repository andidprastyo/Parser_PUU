# PDF Parser and Extractor

This Python script parses PDF files and extracts information from them, saving the extracted data into JSON files.

## Features

- Parses a PDF files
- Extracts text content and divide it into sections
- Saves extracted information into JSON files

### Dependencies

* pdf2image
* pytesseract

### Installation
1. Create a conda virtual environment
   ```
   conda create --name parser-puu python=3.11
   ```
2. Install the dependencies on requirements.txt
   ```
   pip install -r requirements.txt
   ```
3. Install poppler-utils
   ```
   sudo apt-get install poppler-utils
   ```
4. Install poppler via conda
   ```
   conda install -c conda-forge poppler
   ```
5. Run the code
   ```
   python parse_ocr.py
   ```
