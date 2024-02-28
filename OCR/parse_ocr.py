import re
import json
from pdf2image import convert_from_path
import pytesseract

# File paths
pdf_file_path = '../Data/91~PMK.01~2017Per.pdf'
output_json_file = './parsed_data_1.json'
poppler_path = '/usr/bin'

def extract_text_from_pdf(pdf_file_path):
    """Extract text from a PDF file using pytesseract.

    Args:
        pdf_file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    images = convert_from_path(pdf_file_path, poppler_path=poppler_path)
    extracted_text = ''
    for image in images:
        extracted_text += pytesseract.image_to_string(image)
    return extracted_text

def clean_text(text):
    """Clean the given text by removing unwanted characters and patterns.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    patterns = [
        (r'\n+', '\n'),
        (r'\s+', ' '),
        (r'-\s+', '-'),
        (r'_', ''),
        (r'-\d+-', ''),
        (r'-[a-zA-Z]+-', ''),
        (r'\b\w*\\u\w*\b', ''),
        (r'www\.peraturan\.go\.id\s+\d{4},\s+No\.\s+\d+', ''),
        (r'(www\.\S+\s+)\d{4}\b', r'\1'),
        (r'\b(?:https?://|www\.)\S+\b', '')
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def split_content(content_text):
    """Split the content text into sections based on the pattern 'Pasal \d+'.

    Args:
        content_text (str): The text to be split.

    Returns:
        list: A list of sections extracted from the content text.
    """
    content_pattern = re.compile(r'(?:(?<=\.)|(?<=\n)|^)\s*(Pasal \d+)')
    content = re.split(content_pattern, content_text)[1:]
    return content

def parse_text(cleaned_text):
    """Parse the cleaned text and extract relevant information.

    Args:
        cleaned_text (str): The cleaned text to be parsed.

    Returns:
        list: A list of dictionaries containing the parsed information.
            Each dictionary represents a parsed section of the text.
    """
    stop_phrase = "Ditetapkan di Jakarta"
    pattern = re.compile(r'BAB\s+([IVXLCDM]+)[\s\n]+([^0-9]+)\s+Pasal\s+(\d+)', re.IGNORECASE)
    matches = pattern.findall(cleaned_text)

    parsed_text = []

    for match in matches:
        content_match = re.search(fr'{match[1]}(.*?)(?=BAB|\Z)', cleaned_text, re.DOTALL)
        if content_match:
            content = content_match.group(1).strip()
            content = split_content(content)

            for i in range(0, len(content), 2):
                content_number, content_text = content[i], content[i + 1]
                pasal_number = re.search(r'(\d+)', content_number).group(1)

                # References to other pasal
                references = re.findall(r'Pasal\s+(\d+)', content_text)

                additional_context = [{'Text': f'pasal-{ref}'} for ref in references]

                if stop_phrase in content_text:
                    content_text = content_text.split(stop_phrase)[0].strip()

                parsed_text.append({
                    'additional_context': additional_context,
                    'bab': f'bab-{match[0].lower()}',
                    'bagian': 'none',
                    'content': content_text.strip(),
                    'context': match[1],
                    'paragraf': 'none',
                    'pasal': f'pasal-{pasal_number}',
                    'ref': 'none',
                    'type': 'CONTENT_PASAL'
                })

    return parsed_text

def save_to_json(parsed_text, output_file):
    """Save data to a JSON file.

    Args:
        data: Data to be saved.
        output_file (str): Path to the output JSON file.
    """
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(parsed_text, json_file, indent=4)

if __name__ == "__main__":
    extracted_text = extract_text_from_pdf(pdf_file_path)
    cleaned_text = clean_text(extracted_text)
    parsed_content = parse_text(cleaned_text)

    try:
        with open(output_json_file, 'w+', encoding='utf-8') as json_file:
            json.dump(parsed_content, json_file, indent=4)
        print(f"Parsed content saved to {output_json_file}")
    except Exception as e:
        print(f"Error saving parsed content to JSON file: {e}")
