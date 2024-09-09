import tkinter as tk
from tkinter import ttk, Button, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
from fer import FER
import random
import serial
import time
import os
import mysql.connector
from datetime import datetime
from threading import Thread
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import make_interp_spline

# Define the main application class
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Navigation")
        self.attributes("-fullscreen", True)

        # Load an image and resize it
        image = Image.open("C:/Users/DELL/OneDrive/Desktop/clg project/images/workshop.jpg")  
        image = image.resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)
        self.imgtk = ImageTk.PhotoImage(image)

        # Display the image
        label = tk.Label(self, image=self.imgtk)
        label.image = self.imgtk
        label.place(x=0, y=0, relwidth=1, relheight=1)

        proceed_button = Button(self, text="Proceed", command=self.show_menu, bg="#19294A", padx=20, pady=2, fg="white")
        proceed_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="bharat",
            database="stress_detection"
        )
        self.cursor = self.db.cursor()
        self.content_frame = None

    def show_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        menu_frame = tk.Frame(self, bg="darkblue")
        menu_frame.pack(side="top", fill="x")

        buttons = [
            ("Home", self.show_home),
            ("About", self.show_about),
            ("Conclusion", self.show_conclusion),
            ("Detect Stress", self.show_detection),
            ("Results", self.show_results),
        ]

        for (text, command) in buttons:
            button = tk.Button(menu_frame, text=text, command=command, padx=20, pady=10, bg="#0CC0DF", fg="black")
            button.pack(side="left", fill="x", expand=True)

        self.content_frame = tk.Frame(self, bg="#131842")
        self.content_frame.pack(fill="both", expand=True)

        self.show_home()  # Show the home page initially

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_content_frame()
        self.update()
        width, height = self.winfo_width(), self.winfo_height()

        # Load and display the home image
        home_image = Image.open("C:/Users/DELL/OneDrive/Desktop/clg project/images/2.png")
        home_image = home_image.resize((width, height),Image.LANCZOS)
        home_photo = ImageTk.PhotoImage(home_image)

        label = tk.Label(self.content_frame, image=home_photo)
        label.image = home_photo  # Keep a reference to avoid garbage collection
        label.pack(fill="both", expand=True)

    def show_about(self):
        self.clear_content_frame()
        self.update()
        width, height = self.winfo_width(), self.winfo_height()

        # Load and display the about image
        about_image = Image.open("C:/Users/DELL/OneDrive/Desktop/clg project/images/3.png")
        about_image = about_image.resize((width, height), Image.LANCZOS)
        about_photo = ImageTk.PhotoImage(about_image)

        label = tk.Label(self.content_frame, image=about_photo)
        label.image = about_photo  # Keep a reference to avoid garbage collection
        label.pack(fill="both", expand=True)

    def show_conclusion(self):
        self.clear_content_frame()
        self.update()
        width, height = self.winfo_width(), self.winfo_height()

        # Load and display the conclusion image
        conclusion_image = Image.open("C:/Users/DELL/OneDrive/Desktop/clg project/images/5.png")
        conclusion_image = conclusion_image.resize((width, height), Image.LANCZOS)
        conclusion_photo = ImageTk.PhotoImage(conclusion_image)

        label = tk.Label(self.content_frame, image=conclusion_photo)
        label.image = conclusion_photo  # Keep a reference to avoid garbage collection
        label.pack(fill="both", expand=True)

    def show_detection(self):
        self.clear_content_frame()
        detection_page = DetectionPage(self.content_frame, self)  # Pass self as controller
        detection_page.pack(fill="both", expand=True)

    def show_results(self):
        self.clear_content_frame()
        results_page = ResultPage(self.content_frame, self)
        results_page.pack(fill="both", expand=True)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

class DetectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#070F2B')
        self.controller = controller

        card = tk.Frame(self, bg='lightyellow', padx=10, pady=10, bd=2, relief='groove')
        card.pack(pady=20, padx=20, fill="both", expand=True)

        label = tk.Label(card, text="Detect Stress", font=("Helvetica", 16), bg='white')
        label.pack(pady=10, padx=10)

        # User details form
        self.name_label = tk.Label(card, text="Name:", bg='white')
        self.name_label.pack(pady=5)
        self.name_entry = ttk.Entry(card)
        self.name_entry.pack(pady=5)

        self.age_label = tk.Label(card, text="Age:", bg='white')
        self.age_label.pack(pady=5)
        self.age_entry = ttk.Entry(card)
        self.age_entry.pack(pady=5)

        self.submit_button = ttk.Button(card, text="Submit", command=self.save_user_details)
        self.submit_button.pack(pady=20)

        self.start_button = ttk.Button(card, text="Start Detection", command=self.start_detection, state=tk.DISABLED)
        self.start_button.pack(pady=20)

        self.upload_button = ttk.Button(card, text="Upload Media", command=self.upload_media)
        self.upload_button.pack(pady=20)

        self.lbl_video = ttk.Label(card)
        self.lbl_video.pack()

        self.image_frame = tk.Frame(card)
        self.image_frame.pack(pady=20)

        self.lbl_joke = ttk.Label(card, wraplength=400, background='white')
        self.lbl_joke.pack(pady=10)

        self.cap = None
        self.detector = FER(mtcnn=True)
        self.running = False
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why don't skeletons fight each other? They don't have the guts.",
            "What do you get when you cross a snowman and a vampire? Frostbite.",
            "Why did the bicycle fall over? Because it was two-tired!"
        ]
        self.labels = []


        # Initialize serial connection to the pulse sensor
        self.serial_port = 'COM18'  # Change to your actual serial port
        self.baud_rate = 9600
        self.pulse_sensor = None

        # Directory for saving captured images
        self.image_dir = "captured_images"
        os.makedirs(self.image_dir, exist_ok=True)

        # User details
        self.user_id = None

        # BPM Reading
        self.bpm_var = tk.StringVar()
        self.bpm_var.set("0")
        self.bpm_label = tk.Label(card, textvariable=self.bpm_var, font=("Helvetica", 24), bg='white')
        self.bpm_label.pack(pady=10)
        
    def save_user_details(self):
        name = self.name_entry.get()
        age = self.age_entry.get()

        if not name or not age:
            messagebox.showerror("Error", "Please enter your name and age.")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Error", "Age must be an integer.")
            return

        query = "INSERT INTO users (name, age) VALUES (%s, %s)"
        self.controller.cursor.execute(query, (name, age))
        self.controller.db.commit()
        self.user_id = self.controller.cursor.lastrowid
        self.start_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success", "User details saved successfully.")

    def start_detection(self):
        if self.running:
            return
        self.start_button.config(state=tk.DISABLED)
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.pulse_sensor = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
        time.sleep(2)  # Allow time for the serial connection to initialize
        self.bpm_thread = Thread(target=self.update_bpm)
        self.bpm_thread.daemon = True
        self.bpm_thread.start()
        self.capture_and_analyze_images()

    def update_bpm(self):
        while self.running:
            if self.pulse_sensor.in_waiting > 0:
                bpm_data = self.pulse_sensor.readline().decode('utf-8').strip()
                try:
                    bpm_value = int(bpm_data)
                    self.bpm_var.set(str(bpm_value))
                except ValueError:
                    pass
            time.sleep(0.1)

    def capture_and_analyze_images(self):
        images = []
        pulse_readings = []

        for i in range(10):
            ret, frame = self.cap.read()
            if not ret:
                messagebox.showerror("Error", "Failed to capture image")
                break
            images.append(frame)
            self.show_frame_on_label(frame, i)
            pulse_value = self.read_pulse_sensor()
            pulse_readings.append(pulse_value)
            cv2.waitKey(1000)

        self.analyze_images(images, pulse_readings)

    def show_frame_on_label(self, frame, image_counter):
        frame_resized = cv2.resize(frame, (120, 120))
        cv2image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        label = tk.Label(self.image_frame, image=imgtk)
        label.image = imgtk
        label.grid(row=0, column=image_counter, padx=10, pady=10)
        self.labels.append(label)

        self.lbl_video.imgtk = imgtk
        self.lbl_video.configure(image=imgtk)
        self.lbl_video.image = imgtk

        # Save image
        image_path = os.path.join(self.image_dir, f"image_{image_counter}.png")
        img.save(image_path)

    def read_pulse_sensor(self):
        if self.pulse_sensor is not None:
            try:
                pulse_data = self.pulse_sensor.readline().decode('utf-8').strip()
                if pulse_data.isdigit():
                    return int(pulse_data)
            except Exception as e:
                print(f"Error reading pulse sensor: {e}")
        return 0

    def analyze_images(self, images, pulse_readings):
        stress_scores = []
        emotions_detected = []

        for frame in images:
            result = self.detector.detect_emotions(frame)
            if result:
                for face in result:
                    emotions = face['emotions']
                    top_emotion = max(emotions, key=emotions.get)
                    stress_score = emotions.get(top_emotion, 0.0)

                    if top_emotion in ['angry', 'fear', 'disgust', 'sad']:
                        stress_scores.append(stress_score)
                    emotions_detected.append(top_emotion)

        if stress_scores:
            average_stress_score = np.mean(stress_scores)
            if average_stress_score > 0.7:
                stress_level = "High"
                stress_message = "Please take a deep breath and try to relax."
                joke = random.choice(self.jokes)
            elif average_stress_score > 0.4:
                stress_level = "Medium"
                stress_message = "Take a short break, you might be feeling stressed."
                joke = random.choice(self.jokes)
            else:
                stress_level = "Low"
                stress_message = "You seem a bit stressed, try to stay calm."
                joke = ""
        else:
            stress_level = "Not Stressed"
            stress_message = "You seem calm. Keep it up!"
            joke = ""

        average_pulse = np.mean(pulse_readings)
        if average_pulse > 100:
            pulse_message = "Your pulse rate is high. Try to relax."
        elif average_pulse > 80:
            pulse_message = "Your pulse rate is slightly elevated."
        else:
            pulse_message = "Your pulse rate is normal."

        if emotions_detected:
            most_detected_emotion = max(set(emotions_detected), key=emotions_detected.count)
        else:
            most_detected_emotion = "None"

        self.lbl_joke.config(text=joke)
        messagebox.showinfo("Stress Analysis",
                            f"Average Stress Level: {stress_level}\nMost Detected Emotion: {most_detected_emotion}\n\n{stress_message}\n\nAverage Pulse: {average_pulse}\n{pulse_message}")

        # Save stress results to the database
        query = "INSERT INTO stress_results (user_id, stress_score, beats_per_minute, date_recorded) VALUES (%s, %s, %s, %s)"
        self.controller.cursor.execute(query, (self.user_id, average_stress_score, average_pulse, datetime.now()))
        self.controller.db.commit()

        self.stop_detection()

    def stop_detection(self):
        if self.running:
            self.running = False
            self.cap.release()
            self.pulse_sensor.close()
            self.start_button.config(state=tk.NORMAL)

    def upload_media(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi"), ("All files", "*.*")])
        if file_path:
            messagebox.showinfo("Upload Media", f"Media uploaded: {file_path}")


class ResultPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#070F2B')
        self.controller = controller

        card = tk.Frame(self, bg='lightyellow', padx=10, pady=10, bd=2, relief='groove')
        card.pack(pady=20, padx=20, fill="both", expand=True)

        label = tk.Label(card, text="Enter User ID to View Results", font=("Helvetica", 16), bg='white')
        label.pack(pady=10, padx=10)

        self.user_id_label = tk.Label(card, text="User ID:", bg='white')
        self.user_id_label.pack(pady=5)
        self.user_id_entry = ttk.Entry(card)
        self.user_id_entry.pack(pady=5)

        self.fetch_button = ttk.Button(card, text="Fetch Results", command=self.fetch_results)
        self.fetch_button.pack(pady=20)

        self.result_label = tk.Label(card, text="", bg='white', wraplength=400)
        self.result_label.pack(pady=20)

        self.report_button = ttk.Button(card, text="Generate Report", command=self.generate_report, state=tk.DISABLED)
        self.report_button.pack(pady=20)

        self.results = []

    def fetch_results(self):
        user_id = self.user_id_entry.get()
        if not user_id:
            messagebox.showerror("Error", "Please enter a User ID.")
            return

        query = "SELECT * FROM stress_results WHERE user_id = %s"
        self.controller.cursor.execute(query, (user_id,))
        self.results = self.controller.cursor.fetchall()

        if not self.results:
            messagebox.showerror("Error", "No results found for this User ID.")
            return

        result_text = ""
        for result in self.results:
            date_recorded = result[4].strftime("%Y-%m-%d %H:%M:%S")
            result_text += f"Date: {date_recorded}, Stress Score: {result[2]}, BPM: {result[3]}\n"

        self.result_label.config(text=result_text)
        self.report_button.config(state=tk.NORMAL)

    def generate_report(self):
        if not self.results:
            messagebox.showerror("Error", "No results to generate report.")
            return

        # Extract data from results
        dates = [result[4] for result in self.results]  # Assuming index 4 is the date
        stress_scores = [result[2] for result in self.results]  # Assuming index 2 is the stress score
        bpms = [result[3] for result in self.results]  # Assuming index 3 is the BPM

        # Convert dates to a numerical format for interpolation
        date_nums = np.arange(len(dates))

        # Create spline functions for smooth curves
        spline_stress = make_interp_spline(date_nums, stress_scores, k=3)
        spline_bpm = make_interp_spline(date_nums, bpms, k=3)

        # Generate smooth data points
        smooth_dates = np.linspace(0, len(dates) - 1, 300)
        smooth_stress_scores = spline_stress(smooth_dates)
        smooth_bpms = spline_bpm(smooth_dates)

        # Create a figure and axis
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot Stress Score
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Stress Score', color='tab:red')
        ax1.plot(smooth_dates, smooth_stress_scores, color='tab:red', label='Stress Score')
        ax1.tick_params(axis='y', labelcolor='tab:red')
        ax1.set_xticks(date_nums)  # Ensure x-ticks match the dates
        ax1.set_xticklabels(dates, rotation=45)  # Rotate dates for better visibility
        ax1.legend(loc='upper left')

        # Create a second y-axis for BPM
        ax2 = ax1.twinx()
        ax2.set_ylabel('BPM', color='tab:blue')
        ax2.plot(smooth_dates, smooth_bpms, color='tab:blue', linestyle='--', label='BPM')
        ax2.tick_params(axis='y', labelcolor='tab:blue')
        ax2.legend(loc='upper right')

        # Improve layout and add title
        fig.tight_layout()
        plt.title('Stress Score and BPM Over Time', fontsize=16)

        # Display the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class StressDetectionApp(tk.Tk):
    def __init__(self, db_connection):
        super().__init__()
        self.title("Stress Detection")
        self.geometry("800x600")
        
        self.db = db_connection
        self.cursor = self.db.cursor()
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (DetectionPage, ResultPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
