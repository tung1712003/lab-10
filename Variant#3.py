import os, json
import pyttsx3, pyaudio, requests
from vosk import Model, KaldiRecognizer

# Initializing the text-to-speech engine
engine = pyttsx3.Engine()

# Function to perform text-to-speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Initializing and loading the Vosk model
model_path = "vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit(1)
model = Model(model_path)

# Initializing the speech recognizer
recognizer = KaldiRecognizer(model, 16000)

# Initializing PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

# Listening to commands
def listen():
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            return result['text']

# Handling API Requests
def handle_api_request():
    response = requests.get("https://rickandmortyapi.com/api/character/108")
    if response.status_code == 200:
        return response.json()
    else:
        speak("API request failed.")
        return None

# Command functions
def random_character():
    data = handle_api_request()
    if data:
        speak(f"The character's name is {data['name']}")

def save_picture():
    data = handle_api_request()
    if data:
        img_data = requests.get(data['image']).content
        with open('character_image.png', 'wb') as handler:
            handler.write(img_data)
        speak("Image saved successfully.")

def first_episode():
    data = handle_api_request()
    if data:
        episode_url = data['episode'][0]
        episode_response = requests.get(episode_url)
        if episode_response.status_code == 200:
            episode_data = episode_response.json()
            speak(f"The first episode is {episode_data['name']}")
        else:
            speak("Failed to fetch episode data.")

def show_picture():
    data = handle_api_request()
    if data:
        from PIL import Image
        import requests
        from io import BytesIO
        response = requests.get(data['image'])
        img = Image.open(BytesIO(response.content))
        img.show()

# The main function to process the commands
def process_command(command):
    if 'random' in command:
        random_character()
    elif 'save' in command:
        save_picture()
    elif 'episode' in command:
        first_episode()
    elif 'show' in command:
        show_picture()
    else:
        speak("Command not recognized.")

# Loop to continuously listen for commands
while True:
    print("Listening for command...")
    command = listen()
    print(f"Command received: {command}")
    process_command(command)
