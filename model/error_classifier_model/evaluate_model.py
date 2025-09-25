import numpy as np
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from xgboost import XGBClassifier
import joblib
import json
from ocr_extraction import extract_text_from_image

# Load models and data
bert_model = BertForSequenceClassification.from_pretrained("bert_fine_tuned")
tokenizer = BertTokenizer.from_pretrained("bert_fine_tuned")
xgb_model = joblib.load("xgboost_model.pkl")

with open("tasks.json", "r") as f:
    tasks = json.load(f)


def predict_error(image_path):
    """Predicts the error type and suggests tasks related to errors."""
    extracted_text = extract_text_from_image(image_path)

    if not extracted_text:
        return {"error": "No text extracted from image!"}

    inputs = tokenizer(extracted_text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        logits = bert_model(**inputs).logits

    predicted_label = torch.argmax(logits, dim=1).item()
    related_task_id = xgb_model.predict(np.array([[predicted_label]]))[0]

    task = tasks.get(str(related_task_id), {"module_name": "Unknown", "xp": 0, "video_path": "", "steps": []})

    return {
        "error_type": predicted_label,
        "suggested_task": task["module_name"],
        "xp_reward": task["xp"],
        "video_path": task["video_path"],
        "steps": " -> ".join(task["steps"]),
    }


if __name__ == "__main__":
    # Test the pipeline with an image
    image_path = "screenshot.png"  # Replace with your image path
    prediction = predict_error(image_path)
    print("Prediction Results:")
    print(prediction)
