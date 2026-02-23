import cv2
from ultralytics import YOLO
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

model = YOLO('weights/best.pt')

def send_email():
    msg = MIMEText(f'Weapon detected at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    msg['Subject'] = 'ALERT: Weapon Detected'
    msg['From'] = 'mprproj123@gmail.com'
    msg['To'] = 'mprproj123@gmail.com'
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login('mprproj123@gmail.com', 'your_app_password')
            server.send_message(msg)
    except Exception as e:
        print(f'Email error: {e}')

def detect_image(path):
    frame = cv2.imread(path)
    results = model(frame, conf=0.5)
    annotated = results[0].plot()
    if len(results[0].boxes) > 0:
        send_email()
    cv2.imshow('Weapon Detection', annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def detect_video(path):
    cap = cv2.VideoCapture(path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame, conf=0.5)
        annotated = results[0].plot()
        if len(results[0].boxes) > 0:
            send_email()
        cv2.imshow('Weapon Detection', annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def detect_webcam():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame, conf=0.5)
        annotated = results[0].plot()
        if len(results[0].boxes) > 0:
            send_email()
        cv2.imshow('Weapon Detection - Press Q to quit', annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

root = tk.Tk()
root.title('AI Weapon Detection System')
root.geometry('400x300')

tk.Label(root, text='AI Weapon Detection System', font=('Arial', 16, 'bold')).pack(pady=20)

tk.Button(root, text='Detect from Image', width=25, command=lambda: detect_image(filedialog.askopenfilename())).pack(pady=10)
tk.Button(root, text='Detect from Video', width=25, command=lambda: detect_video(filedialog.askopenfilename())).pack(pady=10)
tk.Button(root, text='Start Webcam', width=25, command=detect_webcam).pack(pady=10)

root.mainloop()
