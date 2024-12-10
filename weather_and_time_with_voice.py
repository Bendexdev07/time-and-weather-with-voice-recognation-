import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime, timedelta
import vosk
import sounddevice as sd
import queue
import json

# API Key for OpenWeatherMap
API_KEY = "71d86a3fdb7808ce1cc3bf4b50538830"

# Vosk model setup
MODEL_PATH = r"C:\Users\H O P E\source\repos\itech.py\PythonApplication3\vosk-model-small-en-us-0.15"
vosk.SetLogLevel(-1)
model = vosk.Model(MODEL_PATH)

# Queue for audio data
audio_queue = queue.Queue()

# Callback for microphone input
def audio_callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    audio_queue.put(bytes(indata))

# Function to recognize voice and get city name
def recognize_voice():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=audio_callback):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        print("Listening for your command...")
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text", "")

# Function to fetch weather and time data
def get_weather_and_time(city_name):
    try:
        # API call to fetch weather
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract weather data
        temperature = data['main']['temp']
        condition = data['weather'][0]['description'].capitalize()

        # Calculate local time
        timezone_offset = data['timezone']
        utc_time = datetime.utcnow()
        local_time = utc_time + timedelta(seconds=timezone_offset)

        return f"Weather: {temperature}°C, {condition}", f"Local Time: {local_time.strftime('%Y-%m-%d %H:%M:%S')}"
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error fetching weather data: {e}")
        return None, None

# Function to handle voice command and update the GUI
def handle_voice_command():
    city_name = recognize_voice()
    if city_name:
        weather_info, time_info = get_weather_and_time(city_name)
        if weather_info and time_info:
            weather_label.config(text=weather_info)
            time_label.config(text=time_info)
        else:
            weather_label.config(text="Error fetching weather data.")
            time_label.config(text="")
    else:
        messagebox.showerror("Error", "Could not recognize city name.")

# GUI setup
root = tk.Tk()
root.title("Weather and Time Voice App")
root.geometry("400x300")

title_label = tk.Label(root, text="Weather and Time Voice App", font=("Arial", 16))
title_label.pack(pady=10)

weather_label = tk.Label(root, text="Weather info will appear here.", font=("Arial", 12))
weather_label.pack(pady=10)

time_label = tk.Label(root, text="Time info will appear here.", font=("Arial", 12))
time_label.pack(pady=10)

voice_button = tk.Button(root, text="Get Weather and Time", command=handle_voice_command, font=("Arial", 12))
voice_button.pack(pady=20)

root.mainloop()
