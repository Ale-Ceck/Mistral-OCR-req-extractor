import os
import base64
import json
import io
import logging
from pathlib import Path
from PIL import Image  # For image processing
from mistralai import Mistral, DocumentURLChunk
from mistralai.models import OCRResponse
from IPython.display import display, Markdown


# Setup logging instead of print statements
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MistralOCRProcessor:
    def __init__(self):
        """Initialize the Mistral client with the API key from environment variables."""
        api_key = os.getenv("MISTRALAI_API_KEY")
        if not api_key:
            raise ValueError("MISTRALAI_API_KEY not found in environment variables")
        self.client = Mistral(api_key=api_key)

    @staticmethod
    def encode_image(image_path: str) -> str | None:
        """Encodes an image to base64 format."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            logging.error(f"File not found: {image_path}")
        except Exception as e:
            logging.error(f"Error encoding image: {e}")
        return None

    @staticmethod
    def resize_image_if_needed(image_path: str, max_size_mb=5, output_format="JPEG") -> bytes | None:
        """Resizes an image if it exceeds `max_size_mb` and returns the resized image as bytes."""
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)

        if file_size_mb <= max_size_mb:
            with open(image_path, "rb") as f:
                return f.read()  # No resizing needed

        logging.info(f"Resizing image {image_path} ({file_size_mb:.2f}MB) to fit under {max_size_mb}MB.")

        try:
            img = Image.open(image_path)
            width, height = img.size

            resize_ratio = (max_size_mb * 1024 * 1024 * 0.9) / os.path.getsize(image_path)
            new_width = int(width * resize_ratio ** 0.5)
            new_height = int(height * resize_ratio ** 0.5)

            img = img.resize((new_width, new_height), Image.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format=output_format, quality=85)
            buffer.seek(0)

            return buffer.getvalue()
        except Exception as e:
            logging.error(f"Error resizing image: {e}")
            return None

    def upload_pdf(self, pdf_path: str) -> str:
        """Uploads a PDF file and returns its signed URL."""
        pdf_file = Path(pdf_path).resolve()
        if not pdf_file.is_file():
            raise FileNotFoundError(f"File not found: {pdf_file}")

        if pdf_file.suffix.lower() != ".pdf":
            raise ValueError("Invalid file format. Only PDF files are supported.")

        logging.info(f"Uploading PDF: {pdf_file.name}")

        uploaded_file = self.client.files.upload(
            file={
                "file_name": pdf_file.stem,
                "content": pdf_file.read_bytes(),
            },
            purpose="ocr",
        )

        signed_url = self.client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
        return signed_url.url

    def process_pdf(self, pdf_path: str) -> str:
        """
        Processes a PDF with OCR and returns the extracted markdown.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: Extracted markdown content.
        """
        signed_url = self.upload_pdf(pdf_path)

        logging.info("Performing OCR on the document...")
        pdf_response = self.client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url),
            model="mistral-ocr-latest",
            include_image_base64=True,
        )

        response_dict = json.loads(pdf_response.json())
        json_string = json.dumps(response_dict, indent=4)

        output_path = Path(pdf_path).with_suffix(".json")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_string)
        logging.info(f"OCR output saved to: {output_path}")

        markdown_content = self.get_combined_markdown(pdf_response)
        return markdown_content

    def get_combined_markdown(self, ocr_response: OCRResponse) -> str:
        """Converts OCR output to markdown while embedding base64 images."""
        markdowns = []
        for page in ocr_response.pages:
            image_data = {img.id: img.image_base64 for img in page.images}
            markdowns.append(self.replace_images_in_markdown(page.markdown, image_data))
        return "\n\n".join(markdowns)

    @staticmethod
    def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
        """Replaces image placeholders in markdown with base64-encoded images."""
        for img_name, base64_str in images_dict.items():
            markdown_str = markdown_str.replace(
                f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})"
            )
        return markdown_str


# Allow script to be used as both a module and standalone script
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        logging.error("Usage: python script.py <PDF_PATH>")
        sys.exit(1)

    processor = MistralOCRProcessor()
    markdown_result = processor.process_pdf(sys.argv[1])
    
    # Save markdown output to a file
    output_md_path = Path(sys.argv[1]).with_suffix(".md")
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(markdown_result)
    
    logging.info(f"Markdown output saved to: {output_md_path}")

    # Display markdown output
    display(Markdown(markdown_result))
