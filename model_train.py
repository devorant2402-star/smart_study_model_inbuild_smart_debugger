import os
import json
import pytesseract
import cv2
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from xgboost import XGBClassifier

# Load `tasks.json` file
TASKS_FILE = "tasks.json"
if os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, "r") as file:
        tasks = json.load(file)
    task_categories = {task_id: data.get("module_name", "Unknown") for task_id, data in tasks.items()}
else:
    print("Error: tasks.json not found.")
    tasks = {}
    task_categories = {}

# Load fine-tuned BERT model and tokenizer
try:
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertForSequenceClassification.from_pretrained("model/error_classifier_model")
    model.eval()
except Exception as e:
    print(f"Error loading BERT model: {e}")
    model = None

# Load trained XGBoost model
xgb = XGBClassifier()
try:
    xgb.load_model("model/error_categorization.model")
except Exception as e:
    print(f"Error loading XGBoost model: {e}")


def extract_text_from_image(image_path):
    """Extract text from an image using OCR."""
    if not os.path.exists(image_path):
        print("Error: Image file not found.")
        return ""
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return text.strip()
    except Exception as e:
        print(f"Error processing image: {e}")
        return ""


def classify_error(text):
    """Classify the extracted error text using BERT."""
    if model is None:
        print("Error: BERT model not loaded.")
        return -1
    try:
        tokens = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**tokens)
        predicted_label = torch.argmax(outputs.logits, dim=1).item()
        return predicted_label
    except Exception as e:
        print(f"Error classifying text: {e}")
        return -1


def predict_task_category(label):
    """Predict task category based on the BERT classification output using XGBoost."""
    try:
        return xgb.predict([[label]])[0]
    except Exception as e:
        print(f"Error predicting task category: {e}")
        return "Unknown"


if __name__ == "__main__":
    # Test with a sample image
    image_path = "screenshot.png"  # Replace with actual test image path
    extracted_text = extract_text_from_image(image_path)
    print(f"Extracted Text: {extracted_text}")

    if extracted_text:
        error_label = classify_error(extracted_text)
        if error_label != -1:
            task_category = predict_task_category(error_label)
            print(f"Predicted Error Category: {error_label}")
            print(f"Predicted Task Module: {task_category}")
        else:
            print("Error classification failed.")
    else:
        print("No text detected in the image.")
