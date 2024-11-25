import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import os
import sys
import subprocess
import requests
import bs4
import pyjokes
import cv2
import pywhatkit
from playsound import playsound
from typing import Union
import pyautogui
import tkinter as tk
from tkinter import font, messagebox
import threading
import time
from sys import platform
import io
import socket



# Ensure that sys.stdout has a buffer attribute
if sys.stdout and not hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Similarly for sys.stderr if needed
if sys.stderr and not hasattr(sys.stderr, 'buffer'):
    
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    
def update_answer_box(self, text, color="black"):
    # Ensure text is a string
    text = str(text)
    
    self.answer_box.config(state=tk.NORMAL)
    
    # Define the color tag if not already defined
    self.answer_box.tag_configure("color", foreground=color)
    
    # Insert the text with the color tag
    self.answer_box.insert(tk.END, text + "\n", ("color",))
    
    self.answer_box.yview(tk.END)  # Scroll to the end
    self.answer_box.config(state=tk.DISABLED)


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip is not None:
            self.tooltip.destroy()
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{self.widget.winfo_rootx()+20}+{self.widget.winfo_rooty()+20}")
        label = tk.Label(self.tooltip, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None

class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis AI")
        self.root.configure(bg="#fce4ec")  # Light pink background
        
        # Full screen window
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.quit_fullscreen)
        
        # Main frame
        self.main_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)  # White frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center box where Jarvis answers
        self.answer_box = tk.Text(self.main_frame, height=10, wrap=tk.WORD, font=("Helvetica", 20))
        self.answer_box.pack(pady=20, fill=tk.BOTH, expand=True)
        self.answer_box.config(state=tk.DISABLED, bg="#ffffff", fg="#000000", highlightbackground="#e91e63", highlightcolor="#e91e63", highlightthickness=3)
        
        # Buttons frame
        button_frame = tk.Frame(self.main_frame, bg="#ffffff")
        button_frame.pack(pady=20, fill=tk.X, side=tk.BOTTOM)
        
        # Glowing Start button
        self.start_button = tk.Button(button_frame, text="Start", command=self.start_jarvis, font=("Helvetica", 20, "bold"), bg="#00ff00", fg="#ffffff", activebackground="#32cd32", activeforeground="#ffffff", padx=30, pady=15, relief=tk.RAISED, bd=5)
        self.start_button.pack(side=tk.LEFT, padx=20)
        
        # Glowing Stop button
        self.stop_button = tk.Button(button_frame, text="Stop", command=self.confirm_stop, font=("Helvetica", 20, "bold"), bg="#ff0000", fg="#ffffff", activebackground="#ff4c4c", activeforeground="#ffffff", padx=30, pady=15, relief=tk.RAISED, bd=5)
        self.stop_button.pack(side=tk.LEFT, padx=20)
        
        # Apply tooltips
        Tooltip(self.start_button, "Start Jarvis")
        Tooltip(self.stop_button, "Stop Jarvis")
        
        # Button glow effect
        self.glow_effect(self.start_button, "#00ff00", "#32cd32")
        self.glow_effect(self.stop_button, "#ff0000", "#ff4c4c")
        
        # RGB Glow Effect for the message box border
        self.start_rgb_glow()

        # State tracking
        self.jarvis_thread = None
        self.listening = False

    def glow_effect(self, button, color1, color2):
        def on_enter(e):
            button.config(bg=color2, bd=7)
        
        def on_leave(e):
            button.config(bg=color1, bd=5)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def start_rgb_glow(self):
        def rgb_cycle():
            colors = ["#e91e63", "#f06292", "#ec407a", "#d81b60"]
            while True:
                for color in colors:
                    self.answer_box.config(highlightbackground=color, highlightcolor=color)
                    time.sleep(0.5)
                    
        thread = threading.Thread(target=rgb_cycle, daemon=True)
        thread.start()

    def start_jarvis(self):
        if self.jarvis_thread is None or not self.jarvis_thread.is_alive():
            self.jarvis_thread = threading.Thread(target=self.run_jarvis, daemon=True)
            self.jarvis_thread.start()
            self.listening = True

    def stop_jarvis(self):
        self.listening = False
        self.update_answer_box("Jarvis stopped.\n", "red")
        
    def confirm_stop(self):
        confirm = messagebox.askyesno("Confirm Stop", "Are you sure you want to stop Jarvis?")
        if confirm:
            self.stop_jarvis()
            if self.jarvis_thread:
                self.jarvis_thread.join()

    def run_jarvis(self):
        while self.listening:
            self.update_answer_box("Listening...", "red")
            query = take_command()
            if query != "None":
                self.update_answer_box(f"User: {query}", "red")
                process_command(query, gui=self)  # Pass the GUI object

    def update_answer_box(self, text, color="black"):
        self.answer_box.config(state=tk.NORMAL)
        self.answer_box.insert(tk.END, text + "\n", ("color",))
        self.answer_box.tag_configure("color", foreground=color)
        self.answer_box.yview(tk.END)  # Scroll to the end
        self.answer_box.config(state=tk.DISABLED)

    def quit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

def generate_audio(message: str, voice: str = "Brian") -> Union[None, bytes]:
    url = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={message}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    try:
        result = requests.get(url, headers=headers)
        result.raise_for_status()  # Check if the request was successful
        return result.content
    except requests.RequestException as e:
        print(f"Error fetching audio: {e}")
        return None

def speak(text, voice="Brian", folder="", extension=".mp3"):
    try:
        result_content = generate_audio(text, voice)
        if result_content is None:
            print("Failed to generate audio")
            return "Failed to generate audio"

        file_path = os.path.join(folder, f"{voice}{extension}")
        with open(file_path, "wb") as file:
            file.write(result_content)

        playsound(file_path)
        os.remove(file_path)

        return text
    except Exception as e:
        print(e)
        return str(e)

def take_command():
    r = sr.Recognizer()

    # Adjust the energy threshold to better filter out background noise
    r.energy_threshold = 4000
    r.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = r.listen(source, timeout=4, phrase_time_limit=4)
        except sr.WaitTimeoutError:
            print("Listening timed out")
            return "None"
    
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        query = query.lower()
        print(f"User said: {query}\n")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        return "None"
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return "None"

    return query

def search_google(query):
    try:
        url = f"https://www.google.com/search?q={query}"
        res = requests.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")

        answer = soup.find("div", class_="BNeawe").text
        return answer
    except Exception as e:
        print(f"Google search error: {e}")
        return None

def process_command(query, gui=None):
    # Define a dictionary to store custom commands and their actions
    custom_commands = {
      'jarvis':  lambda: speak("yes sir i am hear to help you your"),  
   'i love you':  lambda: speak("i am sorry but i am already realationship with our team members droid"),
    'tell me about your team member': lambda: speak("There are total 5 members in our groups they are Narayan Bogati Prakash pun Nikita pandey Krishna Aryal and Lok maya"),
        'hello jarvis':  lambda: speak("Hello sir, how can I help you today?"),
        'hello jarvis how are you': lambda: speak("I am good what about you "),
        'i am also fine': lambda: speak("o really nice to meet you"),
        'thank you jarvis ': lambda: speak("welcome sir if you need any further help i am always their for you"),
            'you are boy or girl': lambda: speak("sorry for miss understanding i am ai assistance created by narayan for research and develop"),
        'how are you': lambda: speak("I am fine, sir. Thank you for asking. what about you"),
        'what is your name': lambda: speak("My name is Jarvis, develop by droid group in major project"),
        'who made you': lambda: speak("I was created droid members of CTC college"),
        'jarvis who make you': lambda: speak("I was created droid members of CTC college"),
        'who built you': lambda: speak("I was created droid members of CTC college"),
        'tell me about your team member': lambda: speak("There are total 5 members in our groups they are Narayan BOgati Prakash pun Nikita pandey Krishna Aryal"),
            'who is amul sir': lambda: speak("Amul sir is a  young talented person he is genious in computer field and teach in crimson college of technology  and he live in butwal"),
            'who is amol sir': lambda: speak("Amul sir is a  young talented person he is genious in computer field and teach in crimson college of technology and he is married with his wife few year ago and live in butwal"),
    'who is rajiv sir': lambda: speak("Rajeev sir is a multi talented person who has knowledge about Computer hardware networking software etc He is a teacher of crimson college of technology having greate experience to teach he also focus on practical knowledge "),
         'see the time': lambda: speak(f'Sir, the time is {datetime.datetime.now().strftime("%H:%M:%S")}'),
        'time': lambda: speak(f'Sir, the time is {datetime.datetime.now().strftime("%H:%M:%S")}'),
        'open google': lambda: webbrowser.open('https://google.com'),
        'play music': play_music(),
          'jarvis play music': play_music, 
        'shutdown': lambda: shutdown_system(),
        'stop the system': lambda: stop_jarvis(),
        'jarvis stop the system': lambda: stop_jarvis(),
        'exit': lambda: stop_jarvis(),
         'can i ask some question': lambda: speak("off course why not what do you wan to know "),
         'i have a question': lambda: speak("off course why not what do you wan to know i will help you  "),
          'just tell me who is narayan': lambda: speak("Narayan full name Narayan Bogati he is from pyuthan and he is a skillfull computer engineer hilling from"),
         
       'tell me about you': lambda: speak("I am jarvis you personal assistant to provide you knowledge and do task execute through voice command and created by droid group"),
        'search in youtube': lambda: search_in_youtube(),
        'tell me a joke': lambda: tell_joke(),
        'search in google': lambda: search_in_google(),
        'open file': lambda: open_file_explorer(),
        'close file': lambda: close_file_explorer(),
        'open command': lambda: open_command_prompt(),
        'close command': lambda: close_command_prompt(),
        'open c drive': lambda: open_c_drive(),
        'open vs code': lambda: open_vs_code(),
        'open camera': lambda: open_camera(),
        'jarvis open camera': lambda: open_camera(),
        'close camera': lambda: close_camera(),
        'who is rajendra': lambda: speak("graphic designing and he is from Arghakhanchi"), 
        'open facebook': lambda: speak_and_open('https://www.facebook.com', "Opening facebook"),
        'open youtube': lambda: speak_and_open('https://www.youtube.com', "Opening youtube"),
        'open instagram': lambda: webbrowser.open('https://www.instagram.com'),
        'online shopping': lambda: speak_and_open('https://www.daraz.com.np', "Opening daraz online shopping"),
        'i want to shopping': lambda: speak_and_open('https://www.daraz.com.np', "Opening daraz for online shopping "),
     'check internet speed': lambda: speak_and_open('https://www.fast.com', "opening fast.com to see the speed"),
     'internet speed': lambda: speak_and_open('https://www.fast.com', "opening fast.com to see the speed"),
        'open chat gpt': lambda: webbrowser.open('https://chat.openai.com'),
        'open our website': lambda: webbrowser.open('https://bogatinarayan.github.io/major_project_web/'),
         'i want to download you': lambda: webbrowser.open('https://www.narayanbogati.com.np/jarvis_website/final.html') ,
                
      'play the justin bieber song in youtube': lambda: j_song(),
        'play the justin bieber song': lambda: j_song(),
        'play the relax song': lambda: play_relaxing_song(),
        'play the sushant kc song': lambda: sushant_kc_song(),
        'play the new nepali latest song': lambda: latest_nepali_song(),
        'play nepali song': lambda: latest_nepali_song(),
        'play neplai music': lambda: latest_nepali_song(),
        
        'good morning': lambda: good_morning_routine(),
        'good night' : lambda: good_night_routine(),
        
        'open narayan youtube channel': lambda: speak_and_open('https://www.youtube.com/@narayanbogati2191', "Opening your YouTube channel."),
        'open github': lambda: speak_and_open('https://github.com/', "Opening GitHub."),
        'open narayan website': lambda: speak_and_open('https://www.narayanbogati.com.np/', "Opening your website."),
        'open email': lambda: speak_and_open('https://mail.google.com/mail/u/0/#inbox', "Opening email"),
        'play the latest nepali news': lambda: news_nepal(),
        'play nepali news': lambda: news_nepal(),
        'play latest news': lambda: open_latest_news(),
        'play english news': lambda: open_latest_news(),
        'take screenshot': lambda: (speak("Taking screenshot. Please wait."), take_screenshot()),
        
        'turn on light': lambda: (speak("Turning on the light."), control_led("on")),
        'turn off light': lambda: (speak("Turning off the light"), control_led("off")),
        'light on': lambda: (speak("Turning on the light."), control_led("on")),
        'light off': lambda: (speak("Turning off the light"), control_led("off")),
        

     #this is for my friend detail
     'who is vivek': lambda: speak("He is young geneious person and he is from arghakhanchi and he read in diploma in computer engineer"),
    'who is rajendra': lambda: speak("Rajendra also know as ayush and having nickname raju he is orginally from arghakhanchi and live in butwal he is intrested in graphic  designing "),
    'who is aklesh': lambda: speak("aklesh full name Aklesh yadav he is from kapilvastu He read in diploma in computer engineering in CTC college devinagar "),
    'who is nirdesh': lambda: speak("Nirdesh full name nirdesh shrestha he is from butwal and hava a lot of knowledge about compter"),
    'who is vishal': lambda: speak("Bishal full name Bishal Thapa he is from palpa he is talented person and having skill in all field "),
    'who is akash': lambda: speak("Akash full name akash tharu he is from bardiya nepal and he was also talented person "),
    'who is manish': lambda: speak("Manish full name Manish sanjali he has lot of knowledge including physic,chemistry,math and computer he wnat to make a software engineer"),
    'who is nikita': lambda: speak("Nikita full name Nikita pandey she is from butwal and currently reading in CTC college "),
    'who is krishna':  lambda: speak("Hmm i think that his name is Krishna aryal he is from rupakot gulmi he is currently live in divertol butwal and his nickname is kiss you"),
    'who is mausam': lambda: speak("He is from Bankata butwal he has clear 12 class and he currently read in diploma in computer engineering in CTC college"), 
    
     

  

  
        # Add any additional custom commands here...
    }
    
    # Check for custom commands
    executed = False
    
    for command, action in custom_commands.items():
        if command in query:
            response = action() if callable(action) else action
            if gui and response:
                gui.update_answer_box(response, "blue")

            executed = True
            break
    
    # If no custom command is executed, perform a Google search
    if not executed:
        answer = search_google(query)
        if answer:
            
            if gui:
                gui.update_answer_box(answer, "blue")
            speak(answer)
        else:
            speak("I don't understand, can you tell me again?")
            if gui:
                gui.update_answer_box("I don't understand, can you tell me again?", "red")


# Shutdown the system function by Narayan for Windows and Linux
def shutdown_system():
    speak("Shutting down the system.")
    if platform == "win32":
        os.system('shutdown /p /f')
    elif platform in ["linux", "linux2", "darwin"]:
        os.system('poweroff')
    sys.exit()

# To stop the Jarvis program
def stop_jarvis():
    speak("Stopping the system. Goodbye, sir.")
    sys.exit()


# Function to fetch and tell a joke by PyJokes
def tell_joke(gui=None):
    joke = pyjokes.get_joke()
    print(f"Here's a joke for you: {joke}")
    if gui:
        gui.update_answer_box(joke, "blue")
    speak(f"Here's a joke for you: {joke}")

# Function to search in Google and open in a new tab
def search_in_google():
    speak("What do you want to search for on Google?")
    search_query = take_command()
    if search_query != "None":
        url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open_new_tab(url)
    else:
        speak("Sorry, I didn't catch that. Please try again.")

# Search in YouTube function
def search_in_youtube():
    speak("What do you want to search for on YouTube?")
    search_query = take_command()
    if search_query != "None":
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
    else:
        speak("Sorry, I didn't catch that. Please try again.")

# Function to open a file specified by the user
def open_file_explorer():
    speak("Opening File Explorer.")
    if platform == "win32":
        os.startfile('explorer.exe')
    else:
        speak("Sorry, I can only open File Explorer on Windows.")

def close_file_explorer():
    speak("Closing File Explorer.")
    if platform == "win32":
        try:
            os.system('taskkill /F /IM explorer.exe')
            print("File Explorer closed successfully.")
            # Restart File Explorer if needed
            os.system('start explorer.exe')
        except Exception as e:
            print(f"Error closing File Explorer: {e}")
            speak("Failed to close File Explorer.")
    else:
        speak("Sorry, I can only close File Explorer on Windows.")
        

# Function to open the command prompt
def open_command_prompt():
    speak("Opening command prompt.")
    if platform == "win32":
        os.system('start cmd')
    elif platform == "darwin":
        os.system('open -a Terminal')
    elif platform.startswith("linux"):
        os.system('xdg-open terminal')

# Function to close the command prompt
def close_command_prompt():
    speak("Closing command prompt.")
    if platform == "win32":
        try:
            os.system('taskkill /IM cmd.exe /F')
            print("Command Prompt closed successfully.")
        except Exception as e:
            print(f"Error closing Command Prompt: {e}")
            speak("Failed to close Command Prompt.")
    else:
        speak("Sorry, I can only close Command Prompt on Windows.")


# Function to play music
music_file_path = r"C:\Users\Dell\OneDrive\Documents\Desktop\jarvis_1.5\Music\nam_ko_vana_na.mp3"

def play_music():
    if os.path.exists(music_file_path):
        os.startfile(music_file_path)
    else:
        print("Music file does not exist.")


# Function to open the camera
def open_camera():
    speak("Opening the camera.")
    cap = cv2.VideoCapture(0)  # 0 is typically the index for the default camera

    if not cap.isOpened():
        speak("Sorry, I couldn't access the camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            speak("Failed to grab frame.")
            break

        cv2.imshow('Camera', frame)

        # Press 'q' to close the camera window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Function to close the camera
def close_camera():
    speak("Closing the camera.")
    # Assuming this will be called in context where the camera is being displayed
    cv2.destroyAllWindows()
# Function to play the relaxing song on YouTube
def play_relaxing_song():
    speak("Playing relaxing song on YouTube.")
    pywhatkit.playonyt("relaxing music")  # This will play the first video that matches "relaxing music" on YouTube

# Function to play the Justin Bieber song on YouTube
def j_song():
    speak("Playing Justin Bieber song on YouTube.")
    pywhatkit.playonyt("Justin Bieber music")  

def sushant_kc_song():
    speak("Playing Sushant KC song.")
    pywhatkit.playonyt("Sushant KC song")  

def latest_nepali_song():
    speak("Playing latest Nepali song for you.")
    pywhatkit.playonyt("nepali latest song")

# Function to play Nepali news
def news_nepal():
    speak("Playing the latest Nepali news.")
    pywhatkit.playonyt("play the latest nepali news")




# Function to fetch weather information
def fetch_weather(city, api_key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather_description = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            speak(f"The weather in {city} is {weather_description}. The temperature is {temp} degrees Celsius.")
        else:
            speak("Unable to fetch weather information at the moment.")
    except Exception as e:
        speak(f"Error fetching weather information: {str(e)}")



# Function to open the latest news in the browser
def open_latest_news():
    speak("Opening the latest news in the browser.")
    webbrowser.open('https://news.google.com')





# Function to play the latest news
def play_latest_news():
    speak("Fetching the latest news for you.")
    
    # API URL with your actual API key
    url = "http://newsapi.org/v2/top-headlines?country=us&apiKey=773d70adc027421784ceb0ed14a77efb"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        
        if articles:
            for article in articles[:3]:  # Read out the top 3 articles
                speak(article.get('title', 'No title available'))
                speak("Next news.")
        else:
            speak("Sorry, I couldn't find any news at the moment.")
    else:
        speak("Sorry, I'm unable to fetch the news at the moment.")
    
    speak("See more on the website. Thank you.")


# This is for sound for opening 
def speak_and_open(url, message):
    print(f"Opening URL: {url}")
    webbrowser.open(url)
    speak(message)

# Function to execute the "good morning" routine
def good_morning_routine():
    
    speak("Good morning! Have a great day ahead.")
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {current_time}.")
    play_latest_news()
    fetch_weather("Butwal", "1f824e5f2d0cfc5e79cb78476b4c4471")

# This is for good night 
def good_night_routine():
    speak("Good night, sir. Have a wonderful night.")
    # Ask for tomorrow's schedule
    speak("What's the schedule for tomorrow?")
    tomorrow_schedule = take_command()

    # Store tomorrow's schedule droid group
    if tomorrow_schedule != "None":
        schedule_text = f"Ok sir, I will remember {tomorrow_schedule}. I remain at your service tomorrow."
        print("Tomorrow's schedule:", schedule_text)
        speak(schedule_text)

    pywhatkit.playonyt("good night song")




def remember_message(rememberMessage):
    try:
        with open('data.txt', 'w') as remember:
            remember.write(rememberMessage)
    except Exception as e:
        print(f"Error saving message: {e}")

def recall_message():
    try:
        with open('data.txt', 'r') as remember:
            remembered_message = remember.read()
            return remembered_message
    except Exception as e:
        print(f"Error recalling message: {e}")
        return None

def remember_action():
    speak("What do you want me to remember, Sir?")
    rememberMessage = take_command()
    remember_message(rememberMessage)


def take_screenshot():
    directory_path = r"C:\Users\Dell\OneDrive\Documents\Desktop\jarvis_1.5\jarvis_screenshort"

    # Check if the directory exists; if not, create it droid group
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    screenshot = pyautogui.screenshot()

    # Ask the user for the screenshot file name droid group
    speak("What would you like to name the screenshot file?")
    name = take_command()

    # Validate the input and append the correct file extension (.jpg)
    if name and name != "None":
        if not name.endswith(".jpg"):
            name += ".jpg"
        # Save the screenshot to a file with the correct file extension (.jpg)
        screenshot_path = os.path.join(directory_path, name)
        screenshot.save(screenshot_path, format="JPEG")
        speak(f"Screenshot successfully saved as {name} in folder.")
    else:
        speak("Sorry, I didn't catch that. Please try again.")
        
        #this is for music play
        
music_file_path = r"C:\Users\Dell\OneDrive\Documents\Desktop\jarvis_1.5\Music\nam_ko_vana_na.mp3"

# Function to play music
def play_music():
    if os.path.exists(music_file_path):
       os.startfile(music_file_path)
    else:
        print("Music file does not exist.")


# Function to open the C drive
def open_c_drive():
    speak("Opening C drive.")
    if platform == "win32":
        os.system('start C:')
    else:
        speak("Sorry, I can't open C drive on this platform.")


# Function to open Visual Studio Code
def open_vs_code():
    speak("Opening Visual Studio Code.")
    if platform == "win32":
        os.system('code')  # Assumes VS Code is in the PATH
    elif platform == "darwin":
        subprocess.call(['open', '-a', 'Visual Studio Code'])
    elif platform.startswith("linux"):
        subprocess.call(['code'])
        
       

#this is controlling the light 

# Fix encoding issue
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Resolve ESP32 hostname
def resolve_hostname(hostname):
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        ip_address = addr_info[0][4][0]
        return ip_address
    except socket.gaierror as e:
        print(f"Hostname resolution failed: {e}")
        return None

ESP32_HOSTNAME = "h.local"

# Control the LED on ESP32
def control_led(state):
    esp32_ip = resolve_hostname(ESP32_HOSTNAME)
    if esp32_ip:
        esp32_url = f"http://{esp32_ip}"
        try:
            if state == "on":
                response = requests.get(f"{esp32_url}/led/on")
            elif state == "off":
                response = requests.get(f"{esp32_url}/led/off")
            else:
                raise ValueError("Invalid state. Use 'on' or 'off'.")
            print(response.text)
        except requests.RequestException as e:
            print(f"Error controlling LED: {e}")
    else:
        print("Could not resolve ESP32 hostname.")

 #send email 
 
   
if __name__ == '__main__':
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()
