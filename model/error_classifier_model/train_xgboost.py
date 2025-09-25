import json
import numpy as np
import joblib
from transformers import BertModel, BertTokenizer
from xgboost import XGBClassifier
import torch

# Error sample loader
with open("error_samples.json", "r") as f:
    error_data = json.load(f)

# Initialize BERT
tokenizer = BertTokenizer.from_pretrained("bert_fine_tuned")
model = BertModel.from_pretrained("bert_fine_tuned")


def get_bert_embeddings(text):
    """Extract numerical embeddings using fine-tuned BERT."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()


# Prepare training data
X, y = [], []
task_mapping = {}
for idx, entry in enumerate(error_data):
    text = entry["error_message"]
    task_name = entry["related_task"]

    if task_name not in task_mapping:
        task_mapping[task_name] = len(task_mapping)

    X.append(get_bert_embeddings(text))
    y.append(task_mapping[task_name])

X, y = np.array(X), np.array(y)

# Train XGBoost
xgb = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5)
xgb.fit(X, y)

joblib.dump(xgb, "xgboost_model.pkl")
print("XGBoost model trained and saved!")
