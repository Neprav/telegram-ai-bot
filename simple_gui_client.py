import tkinter as tk
from message_handler import MessageHandler
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Функция для загрузки конфигурации
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def process_message():
    message = user_input.get("1.0", tk.END).strip()  # Получаем текст из Text с учетом нескольких строк
    if not message:
        return
    
    # Загружаем конфиг перед обработкой
    config = load_config()
    handler = MessageHandler(config)

    # Обработка сообщения через модуль message_handler.py
    response = handler.handle_message(message, user_name="Tester")
    
    # Отображение ответа
    response_label.config(text=response)

def clear_fields():
    user_input.delete("1.0", tk.END)  # Очистка поля ввода

# Создание окна приложения
root = tk.Tk()
root.title("Bot Test Client")
root.geometry("400x400")  # Указанный размер окна

# Поле ввода сообщения (многострочное)
tk.Label(root, text="Введите сообщение:").pack(pady=(10, 5))
user_input = tk.Text(root, wrap=tk.WORD, width=50, height=5)  # Поле ввода с переносом строк
user_input.pack(pady=5, padx=10)

# Кнопки отправить и очистить
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="Отправить", command=process_message).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Очистить", command=clear_fields).pack(side=tk.LEFT, padx=5)

# Поле для отображения ответа
response_label = tk.Label(
    root,
    text="",
    wraplength=350,
    justify="left",
    anchor="w",
    bg="white",
    fg="black",
    relief="solid",
    bd=1,  # Толщина рамки
    padx=10,
    pady=10
)
response_label.pack(fill="both", expand=True, padx=10, pady=(10, 20))
response_label.configure(bg="#f0f0f0")  # Серая рамка

# Добавляем обработку Enter для отправки сообщения
def on_enter(event):
    process_message()

user_input.bind("<Return>", on_enter)

# Предотвращение добавления символа новой строки при нажатии Enter
def disable_newline(event):
    return "break"

user_input.bind("<Shift-Return>", lambda _: None)  # Shift+Enter для новой строки
user_input.bind("<Return>", on_enter)  # Enter для отправки
user_input.bind("<Return>", disable_newline, add="+")  # Отключаем новую строку при Enter

# Запуск приложения
root.mainloop()
