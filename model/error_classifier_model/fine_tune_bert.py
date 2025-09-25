from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import torch
from torch.utils.data import Dataset
import json


# Function to load dataset
def load_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    texts = [item["text"] for item in data]
    labels = [item["label"] for item in data]
    unique_labels = sorted(set(labels))
    label_mapping = {label: i for i, label in enumerate(unique_labels)}
    labels = [label_mapping[label] for label in labels]

    return texts, labels, label_mapping


# Function to tokenize texts
def tokenize_texts(texts, tokenizer, max_length=512):
    encodings = tokenizer(
        texts,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    return encodings


# Custom dataset class
class ErrorDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


# Main training function
def train_model():
    # Load training and validation data
    train_file_path = "train_samples.json"
    val_file_path = "val_samples.json"
    print(f"Debug: Loading training data from {train_file_path}...")
    train_texts, train_labels, label_mapping = load_data(train_file_path)
    print(f"Debug: Loading validation data from {val_file_path}...")
    val_texts, val_labels, _ = load_data(val_file_path)

    print(f"Loaded {len(train_texts)} training samples and {len(val_texts)} validation samples.")
    print(f"Label mapping: {label_mapping}")

    # Initialize tokenizer and tokenize data
    print("Debug: Initializing tokenizer...")
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    print("Debug: Tokenizing texts...")
    train_encodings = tokenize_texts(train_texts, tokenizer)
    val_encodings = tokenize_texts(val_texts, tokenizer)

    print(f"Sample tokenized text (train): {train_encodings['input_ids'][0]}")
    print(f"Sample tokenized text (val): {val_encodings['input_ids'][0]}")

    # Wrap data into datasets
    print("Debug: Wrapping datasets...")
    train_dataset = ErrorDataset(train_encodings, train_labels)
    eval_dataset = ErrorDataset(val_encodings, val_labels)

    print(f"First sample in train dataset: {train_dataset[0]}")

    # Initialize the BERT model
    num_labels = len(label_mapping)
    print(f"Debug: Initializing BERT model with {num_labels} labels...")
    model = BertForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        num_labels=num_labels,
    )

    # Define training arguments
    print("Debug: Setting up training arguments...")
    training_args = TrainingArguments(
        output_dir="bert_fine_tuned",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        save_steps=200,
        save_total_limit=2,
        evaluation_strategy="epoch",
        logging_dir="./logs",
        learning_rate=5e-5,
    )

    print(f"Training output directory: {training_args.output_dir}")
    print(f"Evaluation strategy: {training_args.evaluation_strategy}")

    # Initialize the Trainer
    print("Debug: Initializing Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )

    print("Debug: Trainer initialized.")
    print(f"Training samples: {len(train_dataset)}, Validation samples: {len(eval_dataset)}.")

    # Start training
    print("Debug: Starting training...")
    trainer.train()

    print("Debug: Training completed.")
