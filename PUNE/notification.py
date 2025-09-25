import tkinter as tk
import cv2
import pyttsx3
import threading
import json
import os
from PIL import Image, ImageTk
import pytesseract
import joblib
import numpy as np
import torch
from transformers import BertTokenizer, BertModel

# File Paths
QUEST_TRACKING_FILE = r"C:\Users\deven\Downloads\PUNE\PUNE\tasks.json"
USER_PROGRESS_FILE = r"C:\Users\deven\Downloads\PUNE\PUNE\PROGRESS.JSON"
DEFAULT_VIDEO_PATH = r"C:\Users\deven\Downloads\PUNE\PUNE\video\noti.mp4"
IMAGE_PATH = r"C:\Users\deven\Downloads\PUNE\PUNE\images\screenshot.png"
MODEL_PATH = r"C:\Users\deven\Downloads\PUNE\PUNE\model\error_categorization.model"

# Ensure files exist
for file in [QUEST_TRACKING_FILE, USER_PROGRESS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)  # Initialize empty JSON

# Load trained model
try:
    xgb_model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    print("Trained model not found! Please run train_xgboost.py first.")
    exit()

# Load BERT tokenizer & model
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = BertModel.from_pretrained("bert-base-uncased")

def get_bert_embeddings(text):
    """Convert error message text into numerical embeddings using BERT."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()

class QuestNotification:
    def __init__(self, root, quest_id, title, description, reward, difficulty, next_task_info):
        self.root = root
        self.quest_id = quest_id
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry("500x307+1164+660")
        self.root.configure(bg="black")
        self.opacity = 0
        self.root.attributes("-alpha", self.opacity)

        # Shadow window setup
        self.shadow_root = tk.Toplevel()
        self.shadow_root.overrideredirect(True)
        self.shadow_root.attributes("-topmost", True)
        self.shadow_root.geometry("500x307+1175+670")
        self.shadow_root.configure(bg="black")
        self.shadow_root.attributes("-alpha", 0.3)

        # Dragging variables
        self.offset_x = 0
        self.offset_y = 0
        self.root.bind("<Button-1>", self.on_press)
        self.root.bind("<B1-Motion>", self.on_drag)

        # Canvas for video
        self.canvas = tk.Canvas(root, width=500, height=230, highlightthickness=0, bg='black')
        self.canvas.pack()

        # Load Default Video
        self.cap = cv2.VideoCapture(DEFAULT_VIDEO_PATH)
        if not self.cap.isOpened():
            print(f"Error: Cannot open default video file at {DEFAULT_VIDEO_PATH}")
            self.canvas.create_text(250, 115, text="Video Not Available", fill="white", font=("Arial", 16))
            return

        # Store reference to prevent garbage collection
        self.video_image = None

        # Title Label
        self.title_label = tk.Label(root, text=title, font=("Arial", 16, "bold"), fg="cyan", bg="black")
        self.title_label.place(relx=0.5, y=50, anchor=tk.CENTER)

        # Description Label (Animated)
        self.desc_label = tk.Label(root, text="", font=("Arial", 10), fg="white", bg="black", wraplength=450, justify="center")
        self.desc_label.place(relx=0.5, y=90, anchor=tk.CENTER)
        self.animate_text(description)

        # Next Task Info
        self.task_info_label = tk.Label(root, text=f"Next Task: {next_task_info}", font=("Arial", 12, "bold"), fg="cyan", bg="black")
        self.task_info_label.place(relx=0.5, y=150, anchor=tk.CENTER)

        # Difficulty and Reward Labels
        self.difficulty_label = tk.Label(root, text=f"Difficulty: {difficulty}", font=("Arial", 10), fg="white", bg="black")
        self.difficulty_label.place(relx=0.5, y=180, anchor=tk.CENTER)

        self.reward_label = tk.Label(root, text=f"Reward: {reward}", font=("Arial", 10), fg="white", bg="black")
        self.reward_label.place(relx=0.5, y=210, anchor=tk.CENTER)

        # Accept and Decline Buttons
        self.accept_button = tk.Button(root, text="ACCEPT", font=("Arial", 10, "bold"), fg="black", bg="white", command=self.accept_quest)
        self.accept_button.place(relx=0.35, y=240, width=90, height=35)

        self.decline_button = tk.Button(root, text="DECLINE", font=("Arial", 10, "bold"), fg="black", bg="white", command=self.decline_quest)
        self.decline_button.place(relx=0.55, y=240, width=90, height=35)

        # Button to analyze error
        self.analyze_button = tk.Button(root, text="Analyze Error", font=("Arial", 10, "bold"), fg="black", bg="white", command=self.open_error_analyzer)
        self.analyze_button.place(relx=0.5, y=270, anchor=tk.CENTER)

        # Play warrior voice
        threading.Thread(target=self.play_warrior_voice, args=(description,), daemon=True).start()

        # Start video playback
        self.update_frame()

        # Start fade-in animation
        self.fade_in()

    def open_error_analyzer(self):
        """Open the error analyzer window."""
        ErrorAnalyzer(self.root)

    def update_frame(self):
        """Updates the video frame on the Tkinter canvas"""
        try:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video if it ends
                self.root.after(30, self.update_frame)
                return

            frame = cv2.resize(frame, (500, 230))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            self.video_image = ImageTk.PhotoImage(image=img)  # Store reference

            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.video_image)
            self.root.after(30, self.update_frame)
        except Exception as e:
            print(f"Error displaying video frame: {str(e)}")
            self.canvas.create_text(250, 115, text="Video Playback Error", fill="white", font=("Arial", 16))

    def fade_in(self):
        """Gradually increases the window opacity"""
        if self.opacity < 1:
            self.opacity += 0.1
            self.root.attributes("-alpha", self.opacity)
            self.root.after(50, self.fade_in)

    def fade_out(self):
        """Gradually decreases the window opacity and closes it"""
        if self.opacity > 0:
            self.opacity -= 0.1
            self.root.attributes("-alpha", self.opacity)
            self.root.after(50, self.fade_out)
        else:
            self.cap.release()
            self.root.destroy()
            self.shadow_root.destroy()

    def play_warrior_voice(self, text):
        """Plays the quest notification in a deep commander-like voice"""
        engine = pyttsx3.init()
        engine.setProperty('rate', 140)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()

    def animate_text(self, text, index=0):
        """Animates the quest description appearing one letter at a time."""
        if index < len(text):
            self.desc_label.config(text=text[:index + 1])
            self.root.after(50, self.animate_text, text, index + 1)

    def accept_quest(self):
        """Handles quest acceptance and updates user progress"""
        print(f"Quest {self.quest_id} Accepted!")
        self.update_progress(self.quest_id, "accepted")
        self.fade_out()

    def decline_quest(self):
        """Handles quest decline and updates tracking"""
        print(f"Quest {self.quest_id} Declined!")
        self.update_progress(self.quest_id, "declined")
        self.fade_out()

    def update_progress(self, quest_id, status):
        """Updates user progress in the JSON file"""
        try:
            with open(USER_PROGRESS_FILE, "r") as file:
                progress_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            progress_data = {}

        progress_data[quest_id] = status  # Update quest status

        with open(USER_PROGRESS_FILE, "w") as file:
            json.dump(progress_data, file, indent=4)

    def on_press(self, event):
        """Stores the initial click position for dragging"""
        self.offset_x = event.x
        self.offset_y = event.y

    def on_drag(self, event):
        """Moves the window based on the mouse movement"""
        x = self.root.winfo_x() - self.offset_x + event.x
        y = self.root.winfo_y() - self.offset_y + event.y
        self.root.geometry(f"+{x}+{y}")
        self.shadow_root.geometry(f"+{x + 11}+{y + 11}")

class ErrorAnalyzer:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Error Analyzer")
        self.window.geometry("300x200")

        btn_analyze = tk.Button(self.window, text="Analyze Error", command=self.analyze_error, bg="blue", fg="white", font=("Arial", 12))
        btn_analyze.pack(pady=50)

    def analyze_error(self):
        """Analyze error using OCR and XGBoost model."""
        error_text = self.extract_text_from_screenshot()
        if not error_text:
            messagebox.showwarning("No Error", "No error text found in screenshot.")
            return

        # Convert text into BERT embeddings
        error_embedding = get_bert_embeddings(error_text).reshape(1, -1)

        # Predict using trained model
        predicted_label = xgb_model.predict(error_embedding)[0]

        # Display result
        messagebox.showinfo("Error Analysis", f"Predicted Learning Module: {predicted_label}")

    def extract_text_from_screenshot(self):
        """Extract text from the screenshot using OCR."""
        try:
            image = cv2.imread(IMAGE_PATH)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            return text.strip()
        except Exception as e:
            messagebox.showerror("OCR Error", f"Failed to extract text: {str(e)}")
            return None

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    app = QuestNotification(
        root,
        quest_id="Q101",
        title="New Mission: AI Model Training",
        description="Your task is to fine-tune the error detection model for optimal accuracy.",
        reward="500 XP + Special Badge",
        difficulty="Hard",
        next_task_info="Deploy the trained model into production"
    )
    root.mainloop()