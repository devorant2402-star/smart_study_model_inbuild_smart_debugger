import json
from transformers import BertTokenizer


def load_data(file_path):
    """
    Load error messages and their corresponding labels from a JSON file.
    """
    try:
        with open(file_path, "r") as f:
            error_data = json.load(f)

        # Extract error messages and related tasks
        texts = [entry["error_message"] for entry in error_data]
        labels = [entry["related_task"] for entry in error_data]

        # Create a mapping of task names to unique integer labels
        label_mapping = {task: idx for idx, task in enumerate(set(labels))}
        numeric_labels = [label_mapping[label] for label in labels]

        return texts, numeric_labels, label_mapping
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return [], [], {}


def tokenize_texts(texts, tokenizer=None):
    """
    Tokenize the input texts for use in the BERT model.
    """
    if tokenizer is None:
        tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    try:
        tokenized_data = tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        return tokenized_data
    except Exception as e:
        print(f"Error tokenizing texts: {e}")
        return None


if __name__ == "__main__":
    # Example debug usage
    file_path = "error_samples.json"

    print("Loading data...")
    texts, labels, label_mapping = load_data(file_path)
    print(f"Loaded {len(texts)} texts and {len(labels)} labels.")
    print("Label Mapping:", label_mapping)

    print("Initializing tokenizer...")
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    encodings = tokenize_texts(texts, tokenizer)

    print("Sample Tokenized Data:", encodings["input_ids"][:1])
