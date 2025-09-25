import json
from sklearn.model_selection import train_test_split

# Load the dataset
with open("error_samples.json", "r") as file:
    data = json.load(file)

# Split into 80% train and 20% validation
train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)

# Save train and validation data to separate files
with open("train_samples.json", "w") as train_file:
    json.dump(train_data, train_file, indent=4)

with open("val_samples.json", "w") as val_file:
    json.dump(val_data, val_file, indent=4)

print("Successfully split data into train_samples.json and val_samples.json.")
