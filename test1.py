import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
from fer import FER
import random
import numpy as np
import pyttsx3
import serial
import time
import os
import mysql.connector
from datetime import datetime
from threading import Thread
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

        self.engine = pyttsx3.init()

        # Initialize serial connection to the pulse sensor
        self.serial_port = 'COM14'  # Change to your actual serial port
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

        self.result_button = ttk.Button(card, text="View Results", command=self.go_to_results)
        self.result_button.pack(pady=20)

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
                bpm_data = self.pulse_sensor.readline().decode().strip()
                try:
                    bpm_value = int(bpm_data)
                    self.bpm_var.set(str(bpm_value))  # Update GUI with BPM value
                except ValueError:
                    pass  # Handle invalid data gracefully
            
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

    def go_to_results(self):
        self.controller.show_frame("ResultPage")


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

        dates = [result[4] for result in self.results]
        stress_scores = [result[2] for result in self.results]
        bpms = [result[3] for result in self.results]

        fig, ax1 = plt.subplots()

        ax1.set_xlabel('Date')
        ax1.set_ylabel('Stress Score', color='tab:red')
        ax1.plot(dates, stress_scores, color='tab:red', label='Stress Score')
        ax1.tick_params(axis='y', labelcolor='tab:red')

        ax2 = ax1.twinx()
        ax2.set_ylabel('BPM', color='tab:blue')
        ax2.plot(dates, bpms, color='tab:blue', label='BPM')
        ax2.tick_params(axis='y', labelcolor='tab:blue')

        fig.tight_layout()
        plt.title('Stress and BPM Over Time')

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class StressDetectionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stress Detection")
        self.geometry("800x600")
        
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="bharat",
            database="stress_detection"
        )
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

        self.show_frame("DetectionPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    app = StressDetectionApp()
    app.mainloop()
