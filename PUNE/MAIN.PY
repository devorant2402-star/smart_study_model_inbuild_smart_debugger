import tkinter as tk
from idlelib.configdialog import font_sample_text
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import json
import cv2
from PIL import Image, ImageTk
import pyautogui
import pyttsx3  # For voice output
import win32api
import win32con
import win32gui
import pytesseract

class AIModelInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive AI Model Interface")

        # Initialize the pinned state
        self.is_pinned = False

        # Initialize XP
        self.xp_earned = 0

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set window dimensions to 1/3 of screen width and full screen height
        self.window_width = (screen_width // 3) + 37  # Increased width by 37 pixels
        self.window_height = screen_height
        # Position window at the right side of the screen
        window_x = screen_width - self.window_width
        window_y = 0
        self.root.geometry(f"{self.window_width}x{self.window_height}+{window_x}+{window_y}")
        self.root.configure(bg="#000000")
        self.root.attributes("-alpha", 0.7)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.resizable(False, False)

        # Draggable frame
        self.draggable_frame = tk.Frame(root, bg="#222222", width=self.window_width, height=self.window_height)
        self.draggable_frame.place(x=0, y=0)
        self.draggable_frame.bind("<Button-1>", self.start_drag)
        self.draggable_frame.bind("<B1-Motion>", self.drag)

        # Control Frame for Courseware, XP, and Opacity
        self.control_frame = tk.Frame(self.draggable_frame, bg="#222222")
        self.control_frame.grid(row=0, column=0, pady=5, padx=10, sticky="w")

        # Courseware button
        self.courseware_button = ttk.Button(self.control_frame, text="Courseware", command=self.toggle_courseware)
        self.courseware_button.pack(side="left", padx=5)

        # XP Label
        self.xp_label = ttk.Label(self.control_frame, text=f"XP Earned: {self.xp_earned}", font=("Arial", 14),
                                  foreground="white", background="#222222")
        self.xp_label.pack(side="left", padx=5)

        # Opacity Control
        self.opacity = 0.7
        self.opacity_slider = ttk.Scale(self.control_frame, from_=0.3, to=1.0, orient="horizontal",
                                        command=self.update_opacity)
        self.opacity_slider.set(self.opacity)
        self.opacity_slider.pack(side="left", padx=5)

        # Initialize process attribute for mod.py
        self.mod_process = None

        # Video player canvas
        self.video_canvas = tk.Canvas(self.draggable_frame, bg="#111111", width=619, height=364)
        self.video_canvas.grid(row=1, column=0, pady=5, padx=10)

        # Play/Pause button
        self.is_playing = False
        self.play_pause_button = ttk.Button(self.draggable_frame, text="Play", command=self.toggle_play_pause)
        self.play_pause_button.grid(row=2, column=0, pady=5, padx=10)

        # Time Bar (Slider)
        self.time_slider = ttk.Scale(self.draggable_frame, from_=0, to=100, orient="horizontal",
                                     command=self.update_time_slider)
        self.time_slider.grid(row=3, column=0, pady=5, padx=10)

        # Instructions Frame
        self.instructions_frame = tk.Frame(self.draggable_frame, bg="#222222", width=619, height=364)
        self.instructions_frame.grid(row=4, column=0, pady=5, padx=10)

        ttk.Label(self.instructions_frame, text="Step-by-Step Instructions", font=("Arial", 14), foreground="white",
                  background="#222222").pack(pady=5, padx=10)

        self.steps_text = tk.Text(self.instructions_frame, wrap="word", bg="#111111", fg="white", height=10)
        self.steps_text.insert("1.0", "1. Open Chrome\n2. Go to Gmail\n3. Click 'Create Account'")
        self.steps_text.configure(state="disabled")
        self.steps_text.pack(fill="both", pady=5, padx=10)

        ttk.Label(self.instructions_frame, text="Short Task Explanation", font=("Arial", 14), foreground="white",
                  background="#222222").pack(pady=5, padx=10)

        self.short_explanation_text = tk.Text(self.instructions_frame, wrap="word", bg="#111111", fg="white", height=5)
        self.short_explanation_text.insert("1.0",
                                           "This task involves creating a Gmail account by following the provided steps.")
        self.short_explanation_text.configure(state="disabled")
        self.short_explanation_text.pack(fill="both", pady=5, padx=10)

        # Search Frame
        self.search_frame = tk.Frame(self.draggable_frame, bg="#222222", width=619, height=39)
        self.search_frame.grid(row=5, column=0, pady=5, padx=10)

        self.search_label = ttk.Label(self.search_frame, text="Search:", font=("Arial", 14), foreground="white",
                                      background="#222222")
        self.search_label.pack(side="left", padx=10)

        self.search_entry = ttk.Entry(self.search_frame, width=30, font=("Arial", 14))
        self.search_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.search_entry.bind("<Return>", self.perform_search)

        # Frame for buttons
        self.button_frame = tk.Frame(self.draggable_frame, bg="#222222")
        self.button_frame.grid(row=6, column=0, pady=5, padx=10)

        # Added Start Model Training button
        self.train_model_button = ttk.Button(self.button_frame, text="Start Model Training",
                                             command=self.start_model_training)
        self.train_model_button.pack(side="left", padx=5)

        # Buttons for Analyze Error, Click Through, and Extract PDF
        self.error_analysis_button = ttk.Button(self.button_frame, text="Analyze Error", command=self.analyze_error)
        self.error_analysis_button.pack(side="left", padx=5)

        self.extract_pdf_button = ttk.Button(self.button_frame, text="Extract PDF", command=self.extract_pdf)
        self.extract_pdf_button.pack(side="left", padx=5)

        self.click_through_button = ttk.Button(self.button_frame, text="Click Through",
                                               command=self.toggle_click_through)
        self.click_through_button.pack(side="left", padx=5)

        # Error and Solution Frame
        self.error_solution_frame = tk.Frame(self.draggable_frame, bg="#222222", width=619, height=200)
        self.error_solution_frame.grid(row=7, column=0, pady=5, padx=10,)

        self.error_label = tk.Label(self.error_solution_frame, text="Error Message", font=("Arial", 14), bg="#111111",
                                    fg="white")
        self.error_label.pack(pady=5, padx=10, anchor="w")

        self.solution_text = tk.Text(self.error_solution_frame, wrap="word", bg="#111111", fg="white", height=8)
        self.solution_text.insert("1.0", "Error analysis and solution will be displayed here.")
        self.solution_text.configure(state="disabled")
        self.solution_text.pack(fill="both", pady=5, padx=10)

        # Load dataset from JSON file
        self.dataset_path = r"C:\Users\deven\Downloads\PUNE\PUNE\tasks.json"
        self.dataset = self.load_dataset()

        # Initialize the speech engine for voice feedback
        self.engine = pyttsx3.init()

    # Method for starting model training
    def start_model_training(self):
        """
        Simulates starting a machine learning model training process.
        Replace this with your actual model training logic.
        """
        try:
            print("Starting model training...")
            # Add the logic to train your model here
            # For now, simulate with a success message
            messagebox.showinfo("Model Training", "Model training started successfully!")
            print("Model training completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during model training: {e}")

    # Other methods remain unchanged...
    def load_dataset(self):
        try:
            with open(self.dataset_path, "r") as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    raise ValueError("Dataset is not in the expected format.")
                messagebox.showinfo("Success", "Dataset loaded successfully.")
                return data
        except FileNotFoundError:
            messagebox.showerror("Error", "Dataset file not found. Please check the file path.")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Failed to decode JSON. Please ensure the file is correctly formatted.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        return {}


    def update_opacity(self, value):
        self.opacity = float(value)
        self.root.attributes("-alpha", self.opacity)

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def toggle_courseware(self):
        if self.mod_process is None or self.mod_process.poll() is not None:
            self.mod_process = subprocess.Popen(['python', r'C:\Users\deven\Downloads\PUNE\PUNE\mod.py'])
            self.courseware_button.config(text="Close Courseware")
        else:
            self.mod_process.terminate()
            self.mod_process = None
            self.courseware_button.config(text="Courseware")

    def start_drag(self, event):
        """Store offset for dragging."""
        if not self.is_pinned:
            self.x_offset = event.x
            self.y_offset = event.y

    def drag(self, event):
        """Move the window according to mouse movement."""
        if not self.is_pinned:
            x = self.root.winfo_pointerx() - self.x_offset
            y = self.root.winfo_pointery() - self.y_offset
            if x < 0:
                x = 0
            elif x + self.window_width > self.root.winfo_screenwidth():
                x = self.root.winfo_screenwidth() - self.window_width
            if y < 0:
                y = 0
            elif y + self.window_height > self.root.winfo_screenheight():
                y = self.root.winfo_screenheight() - self.window_height
            self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def toggle_play_pause(self):
        if self.is_playing:
            self.is_playing = False
            self.play_pause_button.config(text="Play")
        else:
            self.is_playing = True
            self.play_pause_button.config(text="Pause")
            self.update_video_frame()

    def update_video_frame(self):
        if hasattr(self, 'cap') and self.cap and self.is_playing:
            ret, frame = self.cap.read()
            if ret:
                frame_resized = cv2.resize(frame, (619, 364))
                frame_resized = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_resized)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.video_canvas.imgtk = imgtk
                self.video_canvas.after(10, self.update_video_frame)
            else:
                self.cap.release()
                self.is_playing = False
                self.play_pause_button.config(text="Play")

    def update_time_slider(self, event):
        if hasattr(self, 'cap') and self.cap:
            total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            target_frame = (self.time_slider.get() / 100) * total_frames
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

    def perform_search(self, event=None):
        """Perform search based on voice or text input."""
        search_term = self.search_entry.get().strip().lower()
        print(f"Searching for: {search_term}")  # Debug line

        if not search_term:
            self.speak("Please say or type a task name to search for.")
            return

        data = self.dataset.get(search_term, {})
        if not data:
            self.speak("No results found for the given search term.")
            messagebox.showinfo("Search", "No results found for the given search term.")
            return

        self.video_path = data.get("video_path", "")
        if not self.video_path:
            # Set default notification video path if no video path is found
            self.video_path = r"C:\Users\deven\Downloads\PUNE\PUNE\video\noti.mp4"

        if os.path.exists(self.video_path):
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Failed to open video file.")
                return
            self.update_video_frame()
        else:
            messagebox.showwarning("Warning", f"Video file not found: {self.video_path}")

        self.steps_text.configure(state="normal")
        self.steps_text.delete("1.0", "end")
        for step in data.get("steps", []):
            self.steps_text.insert("end", step + "\n")
        self.steps_text.configure(state="disabled")

        self.short_explanation_text.configure(state="normal")
        self.short_explanation_text.delete("1.0", "end")
        self.short_explanation_text.insert("end", data.get("short_explanation", "No explanation available."))
        self.short_explanation_text.configure(state="disabled")

        # Update XP earned
        self.xp_earned += data.get("xp", 0)
        self.update_xp_label()

    def update_xp_label(self):
        """Update the XP label with the current XP earned."""
        self.xp_label.config(text=f"XP Earned: {self.xp_earned}")
        messagebox.showinfo("XP Earned", f"You have earned {self.xp_earned} XP!")

    def analyze_error(self):
        """
        Analyze errors using screenshots and OCR for troubleshooting support.
        """
        try:
            # Capture and save a screenshot
            screenshot = pyautogui.screenshot()
            screenshot_path = os.path.join(os.getcwd(), "screenshot_error.png")
            screenshot.save(screenshot_path)

            # Validate OCR functionality using pytesseract
            extracted_text = pytesseract.image_to_string(screenshot)

            # Example error detection logic
            if "invalid syntax" in extracted_text.lower():
                error_title = "🔴 Invalid Syntax Detected"
                error_fix = """👉 print("Hello, World!") Check commas, colons, and quote mismatches in your code.
            ✅ Example Fix:
            print("Hello, World!")  # Correct syntax with matching quotes and parentheses
            """
            elif "module not found" in extracted_text.lower():
                error_title = "🔴 Module Not Found"
                error_fix = """👉 Ensure the module is installed.
            ✅ Example Fix:
            pip install beautifulsoup4 requests  # Install missing modules
            """
            elif "nameerror" in extracted_text.lower():
                error_title = "🔴 NameError"
                error_fix = """👉 You're using a variable or function that hasn't been defined yet.
            ✅ Example Fix:
            name = "Python"
            print(name)  # Make sure 'name' is defined before use
            """
            elif "typeerror" in extracted_text.lower():
                error_title = "🔴 TypeError"
                error_fix = """👉 You're using a data type incorrectly. Check function inputs or operations.
            ✅ Example Fix:
            print("The number is " + str(5))  # Convert int to string before concatenation
            """
            elif "indentationerror" in extracted_text.lower():
                error_title = "🔴 Indentation Error"
                error_fix = """👉 Ensure consistent use of spaces/tabs and proper block indentation.
            ✅ Example Fix:
            for i in range(5):
                print(i)  # Proper indentation inside the loop
            """
            elif "zerodivisionerror" in extracted_text.lower():
                error_title = "🔴 Zero Division Error"
                error_fix = """👉 You cannot divide a number by zero.
            ✅ Example Fix:
            num = int(input("Enter a number: "))
            if num != 0:
                print(10 / num)
            else:
                print("Cannot divide by zero")
            """
            elif "filenotfounderror" in extracted_text.lower():
                error_title = "🔴 File Not Found"
                error_fix = """👉 Ensure the file exists in the correct location.
            ✅ Example Fix:
            with open("sample.txt", "r") as file:
                content = file.read()  # Ensure 'sample.txt' exists
            """
            elif "permissionerror" in extracted_text.lower():
                error_title = "🔴 Permission Denied"
                error_fix = """👉 Check file access permissions and run your code as an admin if needed.
            ✅ Example Fix:
            # Try running your script with administrative privileges
            """
            elif "valueerror" in extracted_text.lower():
                error_title = "🔴 Value Error"
                error_fix = """👉 Check for correct input types and valid data values.
            ✅ Example Fix:
            num = input("Enter a number: ")
            if num.isdigit():
                print(int(num))
            else:
                print("Please enter a valid number.")
            """
            else:
                error_title = "🔴 Unknown Error"
                error_fix = """👉 Review your code and debug the issue carefully.
            ✅ Tip: Check syntax, spelling, and indentation line by line.
            """

            # Display error message and solution
            self.solution_text.configure(state="normal")
            self.solution_text.delete("1.0", "end")
            self.solution_text.insert("end", f"{error_title}\n\n{error_fix}")
            self.solution_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during analysis: {str(e)}")

    def toggle_click_through(self):
        if self.is_pinned:
            # Disable click-through (Make the window interactive)
            self.is_pinned = False
            self.root.attributes("-topmost", True)  # Keep window on top
            self.speak("Click-through disabled.")
            self.click_through_button.config(text="Enable Click-Through")

            # Set window to be interactive
            hwnd = self.root.winfo_id()  # Get window handle
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & ~win32con.WS_EX_LAYERED)
            self.root.configure(bg="#000000")  # Restore background color
        else:
            # Enable click-through (Make the window transparent)
            self.is_pinned = True
            self.root.attributes("-topmost", False)  # Allow interaction with elements underneath
            self.speak("Click-through enabled.")
            self.click_through_button.config(text="Disable Click-Through")

            # Set window to be click-through
            hwnd = self.root.winfo_id()  # Get window handle
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 200, win32con.LWA_COLORKEY)
            self.root.configure(bg="#000000")  # Set background color to black for transparency

    def extract_pdf(self):
        """Extract details and update the JSON file."""
        # Open a file dialog to select a PDF file
        pdf_file_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])

        if not pdf_file_path:
            messagebox.showwarning("Warning", "No PDF file selected.")
            return

        # Here you would implement the logic to extract data from the selected PDF file
        # For demonstration, we will just show a message box with the selected file path
        messagebox.showinfo("Selected PDF", f"You selected: {pdf_file_path}")

        # You can implement your PDF extraction logic here
        # For example, using PyPDF2 or pdfplumber to read the PDF content

        # Example of updating the JSON file (you can modify this as needed)
        new_data = {
            "creategmailaccount": {
                "module_name": "Create Gmail Account",
                "difficulty": "easy",
                "xp": 10,
                "video_path": "C:\\Users\\deven\\Downloads\\PUNE\\PUNE\\video\\google.mp4",
                "steps": [
                    "1. Open Chrome",
                    "2. Go to Gmail",
                    "3. Click 'Create Account'"
                ],
                "short_explanation": "This task involves creating a Gmail account by following the provided steps.",
                "reward": "10 points"
            },
            "reset_password": {
                "module_name": "Reset Password",
                "difficulty": "medium",
                "xp": 15,
                "video_path": "path/to/reset_password_video.mp4",
                "steps": [
                    "1. Open Gmail settings",
                    "2. Click 'Change Password'",
                    "3. Enter new password"
                ],
                "short_explanation": "This task involves resetting the Gmail account password by following the steps.",
                "reward": "15 points"
            },
            "setup_two_factor_authentication": {
                "module_name": "Set up Two-Factor Authentication",
                "difficulty": "hard",
                "xp": 20,
                "video_path": "path/to/setup_two_factor_auth_video.mp4",
                "steps": [
                    "1. Go to Security Settings",
                    "2. Click '2-Step Verification'",
                    "3. Follow the steps to set up 2FA"
                ],
                "short_explanation": "This task involves setting up two-factor authentication for added security.",
                "reward": "20 points"
            }
        }

        # Update the JSON file
        try:
            with open(self.dataset_path, "w") as file:
                json.dump(new_data, file, indent=4)
            messagebox.showinfo("Success", "PDF details extracted and JSON file updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update JSON file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AIModelInterface(root)
    root.mainloop()
