import os
import logging
from pathlib import Path
from mistralai import Mistral
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_input_file(filepath):
    """Read input file with error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {str(e)}")
        raise

def get_mistral_response(prompt, model="mistral-large-latest"):
    """
    Get a response from the Mistral AI model for the given prompt.

    Args:
        prompt (str): The text prompt to send to the model
        model (str): The Mistral model to use

    Returns:
        str: The model's response
    """
    try:
        api_key = os.environ.get("MISTRALAI_API_KEY")
        if not api_key:
            raise ValueError("MISTRALAI_API_KEY not found in environment variables")
        
        client = Mistral(api_key=api_key)
        chat_response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return chat_response.choices[0].message.content
    
    except Exception as e:
        logging.error(f"Error calling Mistral API: {str(e)}")
        raise

def save_output(content, output_path):
    """Save the output to a file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Results saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving output: {str(e)}")
        raise

def main():
    # Load environment variables
    load_dotenv()

    # Configure paths
    input_file = 'data/ESA Unclassified/[AD39] JUI-EST-INST-RS-001 Is2.2_JUICE Instruments Reduced Thermal Model Specification.md'
    output_file = 'output/requirements.csv'

    # Create output directory if it doesn't exist
    Path('output').mkdir(exist_ok=True)

    # Read input file
    logging.info(f"Reading input file: {input_file}")
    ocr_text = read_input_file(input_file)

    # Prepare prompt
    prompt = f"""
    Extracted text:
    \n\n
    {ocr_text}
    \n\n
    Extract all requirements from the provided PDF, capturing both the code and the description for each requirement. 
    Structure the output as a table with two fields: 'code' and 'description'. 
    The 'code' should contain the requirement code or identifier.
    The 'description' field should contain the full text of the requirement between brackets.
    Format the output in CSV to ensure compatibility with Excel.
    """

    # Get response from Mistral
    model = "mistral-large-latest"
    logging.info(f"Sending prompt to Mistral {model}")
    response = get_mistral_response(prompt, model)

    # Save results
    save_output(response, output_file)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        exit(1)