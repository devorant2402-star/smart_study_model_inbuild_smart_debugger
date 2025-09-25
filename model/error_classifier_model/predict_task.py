import torch
from transformers import BertTokenizer, BertForSequenceClassification
from error_data_loader import load_data


def predict_error_task(error_message, model, tokenizer, label_mapping):
    """
    Predict the related task for a given error message.
    """
    # Tokenize the input message
    inputs = tokenizer(error_message, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)

    # Get the predicted label
    predicted_label = torch.argmax(outputs.logits, axis=1).item()

    # Map the label back to the task
    task = list(label_mapping.keys())[list(label_mapping.values()).index(predicted_label)]
    return task


if __name__ == "__main__":
    # Load the fine-tuned model and tokenizer
    model = BertForSequenceClassification.from_pretrained("bert_fine_tuned")
    tokenizer = BertTokenizer.from_pretrained("bert_fine_tuned")

    # Load label mapping
    file_path = "error_samples.json"
    _, _, label_mapping = load_data(file_path)

    # Test prediction
    test_error = "SyntaxError: invalid syntax"
    predicted_task = predict_error_task(test_error, model, tokenizer, label_mapping)
    print(f"Predicted Task: {predicted_task}")
