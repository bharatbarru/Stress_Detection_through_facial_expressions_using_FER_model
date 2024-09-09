import tkinter as tk
import serial
import threading

class BPMDisplayApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pulse Sensor BPM Display")
        
        self.bpm_label = tk.Label(self.root, text="BPM: ")
        self.bpm_label.pack()
        
        self.bpm_var = tk.StringVar()
        self.bpm_value_label = tk.Label(self.root, textvariable=self.bpm_var, font=("Helvetica", 24))
        self.bpm_value_label.pack()
        
        self.serial_port = 'COM15'  # Replace with your Arduino's serial port
        self.baud_rate = 9600
        self.serial_connection = None
        self.running = True
        
        # Start a thread to read BPM data from Arduino
        self.bpm_thread = threading.Thread(target=self.read_bpm_from_serial)
        self.bpm_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def read_bpm_from_serial(self):
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            while self.running:
                if self.serial_connection.in_waiting > 0:
                    bpm_data = self.serial_connection.readline().decode().strip()
                    try:
                        bpm_value = int(bpm_data)
                        self.bpm_var.set(f"BPM: {bpm_value}")
                    except ValueError:
                        pass
            self.serial_connection.close()
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
    
    def on_closing(self):
        self.running = False
        if self.serial_connection:
            self.serial_connection.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BPMDisplayApp()
    app.run()
