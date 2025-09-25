import re
import logging
from PIL import Image
import pytesseract

# Configure logging for debugging and tracking
logging.basicConfig(
    filename="error_analysis.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set path to Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class ErrorAnalyzer:
    def __init__(self):
        self.solutions = {
            "FileNotFoundError": [
                "Step 1: Verify the file path is correct.",
                "Step 2: Ensure the file exists at the specified location.",
                "Step 3: Check read permissions for the file."
            ],
            "ValueError": [
                "Step 1: Confirm the input type matches the expected format.",
                "Step 2: If converting to int, ensure the string represents a valid integer."
            ],
            "ImportError": [
                "Step 1: Ensure the required library is installed using pip.",
                "Step 2: Use the command `pip install <library_name>`."
            ],
            "KeyError": [
                "Step 1: Check if the specified key exists in the dictionary.",
                "Step 2: Handle missing keys using `dict.get('<key>')` or exception handling."
            ],
            "AttributeError": [
                "Step 1: Verify that you're calling the correct attribute or method on the object.",
                "Step 2: Ensure the object type matches the attribute/method you're trying to access."
            ],
            "Unknown Error": [
                "The error is unrecognized. Please review the error message for details.",
                "You can consult documentation or research online for potential solutions."
            ]
        }

    def parse_error_message(self, error_message):
        """
        Parse the error message to identify specific error types and details.
        """
        if "FileNotFoundError" in error_message:
            return "FileNotFoundError"
        elif "ValueError:" in error_message:
            match = re.search(r"invalid literal for int\(\) with base 10: '(.*?)'", error_message)
            if match:
                detail = match.group(1)
                return f"ValueError: Invalid input '{detail}'"
            return "ValueError"
        elif "ImportError" in error_message:
            return "ImportError"
        elif "KeyError" in error_message:
            match = re.search(r"KeyError: '(.*?)'", error_message)
            if match:
                return f"KeyError: Missing key '{match.group(1)}'"
            return "KeyError"
        elif "AttributeError" in error_message:
            match = re.search(r"AttributeError: '(.*?)' object has no attribute '(.*?)'", error_message)
            if match:
                obj, attribute = match.groups()
                return f"AttributeError: '{obj}' object missing attribute '{attribute}'"
            return "AttributeError"
        else:
            return "Unknown Error"

    def log_error(self, error_message, solution):
        """
        Log the error message and solution for debugging and tracking purposes.
        """
        logging.debug(f"Error Analyzed: {error_message}")
        logging.debug(f"Solution Provided: {solution}")

    def get_detailed_solution(self, error_type):
        """
        Retrieve a detailed solution for a given error type.
        """
        return self.solutions.get(error_type, ["No solution found for the given error type."])

    def analyze_error(self, error_message):
        """
        Main function to process and analyze the error message.
        """
        logging.info("Starting error analysis...")
        parsed_error = self.parse_error_message(error_message)
        solution_steps = self.get_detailed_solution(parsed_error)

        # Log the error and its solution
        self.log_error(parsed_error, solution_steps)

        return parsed_error, solution_steps


def extract_text_from_image(image_path):
    """
    Perform OCR on an image to extract text using pytesseract.
    """
    try:
        # Load image using PIL
        img = Image.open(image_path)
        # Extract text using pytesseract
        extracted_text = pytesseract.image_to_string(img)
        return extracted_text
    except Exception as e:
        logging.error(f"Error during OCR: {str(e)}")
        return f"Error during OCR: {str(e)}"


def clean_extracted_text(text):
    """
    Preprocess text extracted from OCR or other sources.
    """
    replacements = {
        "\n": " ",
        "ﬁle": "file",  # Correct common OCR errors (e.g., ligatures)
        "ﬁnd": "find"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()


if __name__ == "__main__":
    # Replace with your actual image path
    image_path = r"C:\Users\deven\Downloads\PUNE\PUNE\screenshot_error.png"

    # Perform OCR on the image
    print("Performing OCR on the image...")
    extracted_text = extract_text_from_image(image_path)

    # Optional: Clean the extracted text
    cleaned_text = clean_extracted_text(extracted_text)
    print(f"Extracted Text: {cleaned_text}")

    # Initialize the ErrorAnalyzer
    analyzer = ErrorAnalyzer()

    # Analyze the extracted error
    error_type, solution_steps = analyzer.analyze_error(cleaned_text)

    # Display the results
    print(f"Error Type: {error_type}")
    print("Solution Steps:")
    for step in solution_steps:
        print(step)
