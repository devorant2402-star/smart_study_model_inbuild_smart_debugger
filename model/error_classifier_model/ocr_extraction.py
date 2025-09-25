import cv2
import pytesseract
import os
import re

# Configure the Tesseract executable path (update if needed)
# Ensure this path matches where Tesseract is installed on your system
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR with preprocessing.

    :param image_path: Path to the image file
    :return: Extracted text as a string
    """
    # Load the image
    image = cv2.imread(image_path)

    # Handle case where the image is not loaded (None)
    if image is None:
        raise FileNotFoundError(f"Error: Unable to read the file at {image_path}. Check the path or file integrity.")

    # Convert the image to grayscale for preprocessing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to make the text stand out
    processed_image = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Use Tesseract OCR to extract text
    extracted_text = pytesseract.image_to_string(processed_image).strip()

    return extracted_text


def analyze_error(error_text):
    """
    Analyze the extracted error text and provide potential fixes or suggestions.

    :param error_text: Text extracted from the image
    :return: Suggested fix based on the error
    """
    # Check for SyntaxError
    if "SyntaxError" in error_text:
        match = re.search(r"SyntaxError: (.+)", error_text)
        if match:
            return (f"🔴 **Fix:** {match.group(1)}\n👉 **Solution:** Verify the syntax in the given line 1. use the double quota"
                    f"")

    # Check for NameError
    if "NameError" in error_text:
        match = re.search(r"NameError: name '(.+)' is not defined", error_text)
        if match:
            return f"🔴 **Fix:** Name `{match.group(1)}` is not defined.\n👉 **Solution:** Ensure the variable or function `{match.group(1)}` is defined before you reference it."

    # Check for IndentationError
    if "IndentationError" in error_text:
        match = re.search(r"IndentationError: (.+)", error_text)
        if match:
            return f"🔴 **Fix:** {match.group(1)}\n👉 **Solution:** Verify your indentation level. Ensure consistent use of spaces/tabs."

    # Check for EOF Error (unexpected EOF while parsing)
    if "unexpected EOF while parsing" in error_text:
        return "🔴 **Fix:** Unexpected end of file detected.\n👉 **Solution:** Check for missing closing brackets, quotation marks, or other incomplete code constructs."

    # General case: unrecognized errors
    return "⚠️ Unable to determine the exact issue. Please double-check the error message manually."


if __name__ == "__main__":
    # Input: Path to the image file (Update the path if needed)
    image_path = r"C:\Users\deven\Downloads\PUNE\PUNE\screenshot.png"

    # Check if the file exists before processing
    if not os.path.exists(image_path):
        print(f"Error: File not found at {image_path}. Please provide a valid image path.")
    else:
        try:
            # Step 1: Extract text from the image
            extracted_text = extract_text_from_image(image_path)

            # Step 2: Display the extracted text
            print("Extracted Text:")
            print(extracted_text)

            # Step 3: Analyze errors if any text was extracted
            if extracted_text:
                solution = analyze_error(extracted_text)
                print("\nSolution:")
                print(solution)
            else:
                print("\nNo text was extracted from the image. Make sure the image contains readable error messages.")

        # Handle errors gracefully
        except FileNotFoundError as fnf_error:
            print(f"File not found: {fnf_error}")
        except Exception as e:
            print(f"An error occurred: {e}")
