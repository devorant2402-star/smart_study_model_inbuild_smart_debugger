import tkinter as tk
from PIL import Image, ImageTk
import json
import os
import cv2
import threading
import pyttsx3

# Path Configuration
QUEST_TRACKER_FILE = r"C:\Users\deven\Downloads\PUNE\PUNE\tasks.json"
PROGRESS_FILE = r"C:\Users\deven\Downloads\PUNE\PUNE\PROGRESS.JSON"
DEFAULT_VIDEO_PATH = r'C:\Users\deven\Downloads\PUNE\PUNE\video\noti.mp4'  # Default video for notification


class CoursewareUI:
    def __init__(self, root, user_info, profile_image_path, tasks_file, progress_file):
        self.root = root
        self.root.title("Courseware UI")

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate new window width by reducing 3 cm (~113 pixels) from the right
        self.window_width = screen_width // 3 - 113
        self.window_height = screen_height

        # Initial Position of the window (start position on the screen)
        window_x = 0
        window_y = 0
        self.root.geometry(f"{self.window_width}x{self.window_height}+{window_x}+{window_y}")
        self.root.configure(bg="#000000")
        self.root.attributes("-alpha", 0.9)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.resizable(False, False)

        # Create a Canvas widget with a Scrollbar
        self.canvas = tk.Canvas(self.root, bg="#000000", width=self.window_width, height=self.window_height)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add a Scrollbar to the Canvas
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the Canvas to use the Scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a Frame inside the Canvas to hold the content
        self.draggable_frame = tk.Frame(self.canvas, bg="#000000", width=self.window_width, height=self.window_height)
        self.canvas.create_window((0, 0), window=self.draggable_frame, anchor="nw")

        # User info and profile image
        self.create_profile_display(user_info, profile_image_path)

        # Load task data
        self.tasks_file = tasks_file
        self.progress_file = progress_file
        self.load_task_data()
        self.load_progress()
        self.modules = self.tasks_data
        self.create_modules()

        # Bind the Mouse Wheel to the Canvas for Scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_task_data(self):
        """Loads tasks from the JSON file."""
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r', encoding='utf-8') as file:
                self.tasks_data = json.load(file)
        else:
            self.tasks_data = {}
            print("Warning: tasks.json not found!")

    def load_progress(self):
        """Loads saved student progress."""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as file:
                self.progress_data = json.load(file)
        else:
            self.progress_data = {task: False for task in self.get_all_task_names()}

    def get_all_task_names(self):
        """Get all task names from the modules for progress tracking."""
        task_names = []
        for module_info in self.modules.values():
            for subtopic in module_info.get("steps", []):
                task_names.append(subtopic)
        return task_names

    def create_profile_display(self, user_info, profile_image_path):
        """Displays user profile information."""
        profile_frame = tk.Frame(self.draggable_frame, bg="#000000")
        profile_frame.pack(fill="x", padx=10, pady=10)

        profile_title = tk.Label(profile_frame, text="User    Profile", font=("Arial", 14, "bold"),
                                 bg="#000000", fg="white", anchor="w")
        profile_title.pack(fill="x", pady=5)

        try:
            profile_image = Image.open(profile_image_path)
            profile_image = profile_image.resize((60, 60), Image.Resampling.LANCZOS)
            self.profile_image = ImageTk.PhotoImage(profile_image)  # Keep a reference
            profile_image_label = tk.Label(profile_frame, image=self.profile_image, bg="#000000")
            profile_image_label.pack(side="left", padx=10)
        except Exception as e:
            print(f"Error loading profile image: {e}")
            tk.Label(profile_frame, text="No Image", font=("Arial", 12), fg="white", bg="#000000").pack(side="left", padx=10)

        for key, value in user_info.items():
            tk.Label(profile_frame, text=f"{key.capitalize()}: {value}", font=("Arial", 12),
                     bg="#000000", fg="white", anchor="w").pack(fill="x", pady=2)

    def create_modules(self):
        """Creates vertically stacked modules with subtopics."""
        for module_name, module_info in self.modules.items():
            module_frame = tk.Frame(self.draggable_frame, bg="#000000")
            module_frame.pack(fill="x", padx=10, pady=5)

            module_label = tk.Label(module_frame, text=f"► {module_name}", font=("Arial", 14, "bold"),
                                    bg="#000000", fg="white", anchor="w")
            module_label.pack(side="left", fill="x", expand=True)
            module_label.bind("<Button-1>", lambda e, name=module_name: self.update_d_interface(name))

            progress_frame = tk.Frame(self.draggable_frame, bg="#000000")
            progress_frame.pack(fill="x", padx=20, pady=5)

            for subtopic in module_info.get("steps", []):
                self.create_task(subtopic, progress_frame)

    def create_task(self, task_info, parent_frame):
        """Creates a task widget with a checkbox."""
        task_frame = tk.Frame(parent_frame, bg="#000000")
        task_frame.pack(fill="x", padx=10, pady=2)

        task_var = tk.BooleanVar(value=self.progress_data.get(task_info, False))
        tk.Checkbutton(task_frame, text=f"• {task_info}", font=("Arial", 12), bg="#000000", fg="white",
                       anchor="w", variable=task_var, selectcolor="green",
                       command=lambda: self.save_progress(task_info, task_var.get())).pack(side="left", padx=5)

    def save_progress(self, task_name, completed):
        """Saves progress to the progress file and checks for module completion."""
        self.progress_data[task_name] = completed
        with open(self.progress_file, 'w', encoding='utf-8') as file:
            json.dump(self.progress_data, file, indent=4)

        # Check if the module is completed after marking the task
        module_name = self.get_module_name_from_task(task_name)
        if module_name and self.is_module_completed(module_name):
            self.trigger_notification(module_name)

    def get_module_name_from_task(self, task_name):
        """Finds the module name for a given task."""
        for module_name, module_info in self.modules.items():
            if task_name in module_info.get("steps", []):
                return module_name
        return None

    def is_module_completed(self, module_name):
        """Checks if all tasks in the module are completed."""
        module_info = self.modules.get(module_name, {})
        for task in module_info.get("steps", []):
            if not self.progress_data.get(task, False):
                return False
        return True

    def trigger_notification(self, module_name):
        """Triggers the quest notification for module completion."""
        current_task_data = self.modules.get(module_name, {})
        title = f"Module Completed: {module_name}"
        description = current_task_data.get("short_explanation", "No description available")
        reward = current_task_data.get("reward", "N/A")
        difficulty = current_task_data.get("difficulty", "Unknown")
        next_task_info = self.get_next_task_info(module_name)

        # Check if the video path is valid
        video_path = current_task_data.get('video_path', DEFAULT_VIDEO_PATH)
        if not os.path.exists(video_path):
            print(f"Warning: Video file not found at {video_path}. Using default video.")
            video_path = DEFAULT_VIDEO_PATH

        # Create a new Tkinter window for the notification
        notification_root = tk.Tk()
        QuestNotification(notification_root, title, description, reward, difficulty, next_task_info, video_path)
        notification_root.mainloop()

    def get_next_task_info(self, current_task):
        """Retrieves information about the next task after the current one."""
        task_names = list(self.modules.keys())
        if current_task in task_names:
            current_task_index = task_names.index(current_task)
            next_task_index = current_task_index + 1
            if next_task_index < len(task_names):
                next_task_name = task_names[next_task_index]
                next_task = self.modules[next_task_name]
                return {"module_name": next_task_name,
                        "short_explanation": next_task.get("short_explanation", "No description")}
        return None

    def update_d_interface(self, module_name):
        """Send selected module data to the d.py interface."""
        module_data = self.modules.get(module_name, {})
        if module_data:
            print(f"Updating d.py interface with module: {module_name}")
            print(f"Video Path: {module_data.get('video_path', 'N/A')}")
            print(f"Steps: {module_data.get('steps', [])}")
            print(f"Short Explanation: {module_data.get('short_explanation', 'N/A')}")


class QuestNotification:
    def __init__(self, root, title, description, reward, difficulty, next_task_info, video_path):
        self.root = root
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

        # Load Video with multiple fallback options
        self.cap = None
        video_paths = [
            str(video_path),  # Try provided path first
            str(DEFAULT_VIDEO_PATH),
            'PUNE/video/noti.mp4'  # Explicit default path
        ]
        
        for path in video_paths:
            if os.path.exists(path):
                self.cap = cv2.VideoCapture(path)
                if self.cap.isOpened():
                    print(f"Successfully loaded video from: {path}")
                    break
                else:
                    print(f"Could not open video file at: {path}")
                    self.cap.release()
            else:
                print(f"Video file not found at: {path}")
                
        if not self.cap or not self.cap.isOpened():
            print("Error: Could not load any video file")
            self.show_error_message("Video playback unavailable")
            return

        # Canvas for video
        self.canvas = tk.Canvas(root, width=500, height=230, highlightthickness=0)
        self.canvas.pack()

        # Title Label
        self.title_label = tk.Label(root, text=title, font=("Arial", 16, "bold"), fg="cyan", bg="black")
        self.title_label.place(relx=0.5, y=50, anchor=tk.CENTER)

        # Description Label (Animated)
        self.desc_label = tk.Label(root, text="", font=("Arial", 10), fg="white", bg="black", wraplength=450,
                                   justify="center")
        self.desc_label.place(relx=0.5, y=90, anchor=tk.CENTER)
        self.animate_text(description)

        # Next Task Info
        self.task_info_label = tk.Label(root, text=f"Next Task: {next_task_info}", font=("Arial", 12, "bold"),
                                        fg="cyan", bg="black")
        self.task_info_label.place(relx=0.5, y=150, anchor=tk.CENTER)

        # Difficulty and Reward Labels
        self.difficulty_label = tk.Label(root, text=f"Difficulty: {difficulty}", font=("Arial", 10), fg="white",
                                         bg="black")
        self.difficulty_label.place(relx=0.5, y=180, anchor=tk.CENTER)

        self.reward_label = tk.Label(root, text=f"Reward: {reward}", font=("Arial", 10), fg="white", bg="black")
        self.reward_label.place(relx=0.5, y=210, anchor=tk.CENTER)

        # Accept and Decline Buttons
        self.accept_button = tk.Button(root, text="ACCEPT", font=("Arial", 10, "bold"), fg="black", bg="white",
                                       command=self.accept_quest)
        self.accept_button.place(relx=0.35, y=240, width=90, height=35)

        self.decline_button = tk.Button(root, text="DECLINE", font=("Arial", 10, "bold"), fg="black", bg="white",
                                        command=self.decline_quest)
        self.decline_button.place(relx=0.55, y=240, width=90, height=35)

        # Play warrior voice
        threading.Thread(target=self.play_warrior_voice, args=(description,), daemon=True).start()

        # Initialize video reference storage
        self.video_images = []  # Keep references to all created images
        self.current_image = None

        # Start video playback
        self.update_frame()

        # Start fade-in animation
        self.fade_in()

    def show_error_message(self, message):
        """Displays an error message on the canvas"""
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, 500, 230, fill="black")
        self.canvas.create_text(250, 115, text=message, fill="white", font=("Arial", 16))

    def update_frame(self):
        """Updates the video frame on the Tkinter canvas"""
        if not self.cap or not self.cap.isOpened():
            self.show_error_message("Video playback error")
            self.root.after(1000, self.update_frame)  # Retry after delay
            return
            
        try:
            ret, frame = self.cap.read()
            if not ret:
                # Restart video from beginning
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.root.after(30, self.update_frame)
                return

            frame = cv2.resize(frame, (500, 230))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Create and store the PhotoImage with a proper reference
            if not hasattr(self, 'current_frame_image'):
                self.current_frame_image = ImageTk.PhotoImage(image=img)
            else:
                self.current_frame_image.paste(img)  # Reuse existing PhotoImage
            
            self.canvas.delete("all")
            self.canvas.create_rectangle(0, 0, 500, 230, fill="black")  # Black background
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_frame_image)
            self.root.after(30, self.update_frame)
        except Exception as e:
            print(f"Error displaying video frame: {str(e)}")
            self.canvas.delete("all")
            self.canvas.create_rectangle(0, 0, 500, 230, fill="black")  # Black background
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
        print("Quest Accepted!")
        self.fade_out()

    def decline_quest(self):
        print("Quest Declined!")
        self.fade_out()

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


if __name__ == "__main__":
    user_info = {"name": "John Doe", "email": "johndoe@example.com", "course_id": "C12345"}
    profile_image_path = r"C:\Users\deven\Downloads\PUNE\PUNE\images\pyimage1.png"
    tasks_file = r"C:\Users\deven\Downloads\PUNE\PUNE\tasks.json"
    progress_file = r"C:\Users\deven\Downloads\PUNE\PUNE\progress.json"

    root = tk.Tk()
    app = CoursewareUI(root, user_info, profile_image_path, tasks_file, progress_file)
    root.mainloop()