import tkinter as tk
from message_handler import MessageHandler
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to load configuration
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def process_message():
    message = user_input.get("1.0", tk.END).strip()  # Get text from Text widget including multiple lines
    if not message:
        return
    
    # Load config before processing
    config = load_config()
    handler = MessageHandler(config)

    # Process message through message_handler.py module
    response = handler.handle_message(message, user_name="Tester")
    
    # Display response
    response_label.config(text=response)

def clear_fields():
    user_input.delete("1.0", tk.END)  # Clear input field

# Create application window
root = tk.Tk()
root.title("Bot Test Client")
root.geometry("400x400")  # Set window size

# Message input field (multiline)
tk.Label(root, text="Enter message:").pack(pady=(10, 5))
user_input = tk.Text(root, wrap=tk.WORD, width=50, height=5)  # Input field with word wrap
user_input.pack(pady=5, padx=10)

# Send and Clear buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="Send", command=process_message).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Clear", command=clear_fields).pack(side=tk.LEFT, padx=5)

# Response display field
response_label = tk.Label(
    root,
    text="",
    wraplength=350,
    justify="left",
    anchor="w",
    bg="white",
    fg="black",
    relief="solid",
    bd=1,  # Border width
    padx=10,
    pady=10
)
response_label.pack(fill="both", expand=True, padx=10, pady=(10, 20))
response_label.configure(bg="#f0f0f0")  # Gray border

# Add Enter key handler for sending message
def on_enter(event):
    process_message()

user_input.bind("<Return>", on_enter)

# Prevent adding newline character when pressing Enter
def disable_newline(event):
    return "break"

user_input.bind("<Shift-Return>", lambda _: None)  # Shift+Enter for new line
user_input.bind("<Return>", on_enter)  # Enter to send
user_input.bind("<Return>", disable_newline, add="+")  # Disable newline on Enter

# Run application
root.mainloop()
