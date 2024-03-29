import threading

import customtkinter as ctk
from openai import OpenAI

client = OpenAI()
import tkinter as tk
from tkinter import ttk

from recorder.audio import AudioRecorder
from .views import *

enhancements_prompts = {
    "Grammar": "Can you edit the grammar in my essay?",
    "Phrasing": "Can you edit the phrasing in my essay to sound more impressive?"
}
suggestion_prompts = {
    "Suggestions": "Can you give me suggestions to improve my essay?",
    "Feedback": "Can you give me feedback on my essay?",
    "Counters": "What are some counterarguments to the main points in my essay?",
}

class App(ctk.CTk):
    view_list = {}
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Init models
        self.messages = [ {"role": "system", "content": "You are a intelligent assistant"} ]
        self.audio_recorder = AudioRecorder()
        
        # Setup window
        super().__init__(fg_color= "black")
        self.attributes("-fullscreen", True)
        self.attributes("-type", "splash")
        
        # Setup views
        HomeScreen(self)
        RecordingScreen(self)
        StopScreen(self)
        Editing(self)
        Stats(self)
        
        # Setup popup
        self.prompt = Prompt(self)
        
        self.set_view("home")
        message = "Winston Churchill is widely regarded as one of the most effective leaders of the 20th century, particularly for his leadership during World War Il. However, what made Churchill's leadership style so successful? One way to answer this question is by"
        self.view_list["editing"].text_frame.text.set(message)
        
        self.mainloop()
        
    def set_view(self, pointer: str):
        try:
            self.view_list[pointer].tkraise()
        except KeyError:
            raise ValueError(f"Unknown view '{pointer}'")
        
    def record(self):
        self.recording_thread = threading.Thread(target=self.audio_recorder.record)
        self.recording_thread.start()
        self.play()
        
    def play(self):
        self.audio_recorder.paused = False
        self.set_view("recording_screen")
            
    def pause(self):
        self.audio_recorder.paused = True
        self.set_view("stop_screen")
        
    def stop(self):
        self.audio_recorder.stopped = True
        self.recording_thread.join()
        transcript = self.audio_recorder.process()
        self.view_list["editing"].text_frame.text.set(transcript)
        self.set_view("editing")
        
        
    def edit(self, option: str, output: ctk.StringVar):
        if option in enhancements_prompts.keys():
            prompt = enhancements_prompts[option]
            edit = "enhance"
        elif option in suggestion_prompts.keys():
            prompt = suggestion_prompts[option]
            edit = "suggest"
        message = output.get()
        total_input = f"{prompt}\n\n{message}"
        
        if message and option:
            self.messages.append({"role": "user", "content": total_input})
            chat = client.chat.completions.create(model="gpt-3.5-turbo", 
            messages=[
                {
                    "role": "user",
                    "content": total_input
                }
            ], 
            max_tokens=1000) 
            reply = chat.choices[0].message.content
            
            if edit == "enhance":
                output.set(reply)
            elif edit == "suggest":
                self.prompt.text_frame.text.set(reply)
                self.prompt.show()