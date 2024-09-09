import tkinter as tk
from tkinter import ttk, Button, messagebox, filedialog
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

# Function to show different pages with content
def show_placeholder_page(page_name):
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    if page_name == "home":
        card_frame = tk.Frame(content_frame, bg="#F8DE22", bd=1, relief=tk.SOLID)
        card_frame.pack(padx=20, pady=20, fill="both", expand=True)

        heading = tk.Label(card_frame, text="Abstract", bg="#F8DE22", font=("Helvetica", 18, "bold"), padx=10, pady=10)
        heading.pack()

        label_text = """                        
        Our system features a cutting-edge stress detection system that leverages facial expression analysis to identify three levels of stress: mild, moderate, and severe. Based on these detections, it offers tailored advice to help individuals manage their stress effectively. Initial tests have shown promising results, indicating that our system provides a convenient way for users to handle stress independently.

        The core of our system is powered by state-of-the-art machine learning algorithms, which analyze facial expressions in real-time. This allows the system to provide immediate feedback and personalized suggestions based on the detected stress level. Our ultimate goal is to make stress management more accessible and user-friendly for everyone.

        To enhance user experience, the personalized messages are crafted to motivate and guide users through various stress-relief techniques. Looking ahead, future updates will focus on improving the accuracy of our stress detection capabilities and integrating our system with other health monitoring platforms, ensuring a more comprehensive approach to stress management.
        """

        label = tk.Label(card_frame, text=label_text, bg="white", font=("Helvetica", 16), padx=10, pady=10, justify="left", wraplength=700)
        label.pack(fill="both", expand=True)

    elif page_name == "about":
        card_frame = tk.Frame(content_frame, bg="#102C57", bd=1, relief=tk.SOLID)
        card_frame.pack(padx=20, pady=20, fill="both", expand=True)

        heading = tk.Label(card_frame, text="About AI/ML and CNN", bg="#102C57", font=("Helvetica", 18, "bold"), padx=10, pady=10)
        heading.pack()

        about_text = """
        Artificial Intelligence (AI) and Machine Learning (ML) are revolutionary fields that have transformed numerous industries. AI refers to the simulation of human intelligence in machines programmed to think and learn. ML, a subset of AI, involves training algorithms to make predictions or decisions without being explicitly programmed to perform those tasks.

        Convolutional Neural Networks (CNNs) are a class of deep learning algorithms particularly effective in processing data with a grid-like topology, such as images. CNNs are designed to automatically and adaptively learn spatial hierarchies of features through backpropagation by using multiple building blocks, such as convolution layers, pooling layers, and fully connected layers.

        CNNs have been widely used in various applications:
        Image Recognition: Identifying objects within images with high accuracy.
        Facial Recognition: Analyzing facial features for identification and verification.
        Medical Image Analysis: Assisting in diagnosing diseases by analyzing medical scans.
        Autonomous Vehicles: Helping in object detection and navigation for self-driving cars.
        Natural Language Processing (NLP): Enhancing tasks like translation and sentiment analysis.

        The strength of CNNs lies in their ability to learn important features directly from data, making them an essential tool in modern AI applications. They reduce the need for manual feature extraction, making it easier to develop and deploy AI solutions.
        """

        label = tk.Label(card_frame, text=about_text, bg="lightyellow", font=("Helvetica", 16), padx=10, pady=10, justify="left", wraplength=700)
        label.pack(fill="both", expand=True)

    elif page_name == "conclusion":
        card_frame2 = tk.Frame(content_frame, bg="#F8DE22", bd=1, relief=tk.SOLID)
        card_frame2.pack(padx=20, pady=20, fill="both", expand=True)
        
        heading = tk.Label(card_frame2, text="Conclusion", bg="#F8DE22", font=("Helvetica", 18, "bold"), padx=10, pady=10)
        heading.pack()

        label_text = """
        In conclusion, our project demonstrates the significant potential of using advanced machine learning algorithms, specifically Convolutional Neural Networks (CNNs), to detect and manage stress through facial expression analysis. The system we developed is capable of identifying three levels of stress: mild, moderate, and severe, and provides tailored advice to help individuals manage their stress effectively.

        Initial testing has shown promising results, indicating that the system is a convenient and effective tool for independent stress management. By leveraging real-time facial expression analysis, the system provides immediate feedback and personalized suggestions, making stress management more accessible and user-friendly.

        The integration of state-of-the-art machine learning techniques allows our system to learn and adapt to individual users, improving its accuracy and effectiveness over time. As we look to the future, we aim to enhance the system further by improving its detection capabilities and integrating it with other health monitoring platforms. This will provide a more comprehensive approach to stress management, ensuring users receive the most accurate and personalized support possible.

        Overall, this project not only highlights the capabilities of modern AI and machine learning technologies but also underscores their potential to make a positive impact on mental health and well-being. We are excited about the future possibilities and are committed to continuing our work to improve and expand this system.
        """

        label = tk.Label(card_frame2, text=label_text, bg="#102C57", font=("Helvetica", 16), padx=10, pady=10, justify="left", wraplength=700)
        label.pack(fill="both", expand=True, anchor='w')

    elif page_name == "predict":
        detection_page = DetectionPage(content_frame, root)
        detection_page.pack(fill="both", expand=True)

# Function to initialize and show the main menu
def show_menu():
    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    # Display menu frame
    menu_frame = tk.Frame(root, bg="darkblue")
    menu_frame.pack(side="top", fill="x")
    
    # Menu buttons
    home_button = tk.Button(menu_frame, text="Home", command=lambda: show_placeholder_page("home"), padx=20, pady=10, bg="#0CC0DF", fg="black")
    home_button.pack(side="left", fill="x", expand=True)
    
    about_button = tk.Button(menu_frame, text="About", command=lambda: show_placeholder_page("about"), padx=20, pady=10, bg="lightyellow", fg="black")
    about_button.pack(side="left", fill="x", expand=True)
    
    conclusion_button = tk.Button(menu_frame, text="Conclusion", command=lambda: show_placeholder_page("conclusion"), padx=20, pady=10, bg="#0CC0DF", fg="black")
    conclusion_button.pack(side="left", fill="x", expand=True)
    
    predict_button = tk.Button(menu_frame, text="Detect Stress", command=lambda: show_placeholder_page("predict"), padx=20, pady=10, bg="lightyellow", fg="black")
    predict_button.pack(side="left", fill="x", expand=True)
    
    global content_frame
    content_frame = tk.Frame(root, bg="#131842")
    content_frame.pack(fill="both", expand=True)
    
    show_placeholder_page("home")  # Show the home page initially

# Initialize tkinter window
root = tk.Tk()
root.title("Tkinter Navigation")

# Set the window to full-screen mode
root.attributes("-fullscreen", True)

# Load an image and resize it to fit the screen dimensions
# Replace with your image path
image = Image.open("C:/Users/DELL/OneDrive/Desktop/clg project/images/workshop.jpg")  
image = image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)  # Use Image.LANCZOS for resizing
imgtk = ImageTk.PhotoImage(image)

# Display the image using a Label that fills the entire screen
label = tk.Label(root, image=imgtk)
label.image = imgtk  # Keep a reference to avoid garbage collection
label.place(x=0, y=0, relwidth=1, relheight=1)  # Use place() to cover the whole window

# Example Proceed button, placed over the image
proceed_button = Button(root, text="Proceed", command=show_menu, bg="#19294A", padx=20, pady=2, fg="white")
proceed_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)  # Place button at the bottom center of the window

class DetectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#070F2B')
        self.controller = controller

        card = tk.Frame(self, bg='lightyellow', padx=10, pady=10, bd=2, relief='groove')
        card.pack(padx=20, pady=20, fill='both', expand=True)

        title = tk.Label(card, text="Stress Detection", font=("Helvetica", 24, "bold"), bg='lightyellow')
        title.pack()

        form_frame = tk.Frame(card, bg='lightyellow')
        form_frame.pack(pady=20)

        name_label = tk.Label(form_frame, text="Name:", font=("Helvetica", 18), bg='lightyellow')
        name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = tk.Entry(form_frame, font=("Helvetica", 18))
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        age_label = tk.Label(form_frame, text="Age:", font=("Helvetica", 18), bg='lightyellow')
        age_label.grid(row=1, column=0, padx=10, pady=10)
        self.age_entry = tk.Entry(form_frame, font=("Helvetica", 18))
        self.age_entry.grid(row=1, column=1, padx=10, pady=10)

        self.camera_label = tk.Label(card, text="Camera Feed", bg="lightyellow")
        self.camera_label.pack(pady=10)

        self.start_button = tk.Button(card, text="Start Detection", font=("Helvetica", 18), command=self.start_detection)
        self.start_button.pack(pady=10)

        self.result_label = tk.Label(card, text="", font=("Helvetica", 18), bg="lightyellow")
        self.result_label.pack(pady=10)

        self.canvas = None

    def show_result(self, stress_score, bpm):
        self.result_label.config(text=f"Stress Level: {stress_score}, BPM: {bpm}")

    def start_detection(self):
        name = self.name_entry.get()
        age = self.age_entry.get()

        if not name or not age:
            messagebox.showerror("Input Error", "Please enter both name and age.")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid age.")
            return

        # Start the detection process
        self.capture_images(name, age)

    def capture_images(self, name, age):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Unable to access the camera.")
            return

        count = 0
        captured_images = []
        while count < 10:
            ret, frame = cap.read()
            if ret:
                captured_images.append(frame)
                count += 1
                time.sleep(1)
            else:
                messagebox.showerror("Capture Error", "Failed to capture image.")
                break
        cap.release()

        if len(captured_images) == 10:
            stress_score = self.analyze_images(captured_images)
            bpm = self.measure_bpm()
            self.save_results(name, age, stress_score, bpm)
            self.show_result(stress_score, bpm)
        else:
            messagebox.showerror("Capture Error", "Failed to capture 10 images.")

    def analyze_images(self, images):
        detector = FER(mtcnn=True)
        total_stress_score = 0
        for img in images:
            result = detector.detect_emotions(img)
            if result:
                emotions = result[0]['emotions']
                stress_score = emotions.get('sad', 0) + emotions.get('angry', 0) + emotions.get('disgust', 0)
                total_stress_score += stress_score
        average_stress_score = total_stress_score / len(images)
        return round(average_stress_score, 2)

    def measure_bpm(self):
        try:
            ser = serial.Serial('COM3', 9600, timeout=2)
            ser.flushInput()
            bpm_data = []
            start_time = time.time()
            while time.time() - start_time < 10:
                if ser.inWaiting() > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    try:
                        bpm = float(line)
                        bpm_data.append(bpm)
                    except ValueError:
                        continue
            ser.close()
            average_bpm = sum(bpm_data) / len(bpm_data) if bpm_data else 0
            return round(average_bpm, 2)
        except serial.SerialException:
            messagebox.showerror("Serial Error", "Failed to read from serial port.")
            return 0

    def save_results(self, name, age, stress_score, bpm):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="bharat",
            database="stress_detection"
        )
        cursor = conn.cursor()
        user_id = random.randint(1000, 9999)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO results (user_id, name, age, stress_score, bpm, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, name, age, stress_score, bpm, timestamp))

        conn.commit()
        cursor.close()
        conn.close()

# Run the application
show_menu()
root.mainloop()
