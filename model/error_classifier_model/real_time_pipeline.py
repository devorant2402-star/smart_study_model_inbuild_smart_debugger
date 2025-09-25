import subprocess


def fine_tune_bert():
    subprocess.run(["python", "fine_tune_bert.py"])


def train_xgboost():
    subprocess.run(["python", "train_xgboost.py"])


def run_pipeline():
    print("Updating models...")
    fine_tune_bert()
    train_xgboost()
    print("Models updated successfully!")


if __name__ == "__main__":
    run_pipeline()
