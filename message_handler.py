import random
import re
import time
import logging
import os
from google import genai

class MessageHandler:
    def __init__(self, config):
        self.config = config
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY не задан! Проверьте переменные окружения.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_config = {
            "temperature": 1.4,
            "top_p": 0.99,
            "top_k": 0,
            "max_output_tokens": 4096,
        }

    def is_insult(self, text):
        pattern = r'\b(' + '|'.join(re.escape(word) for word in self.config['insults']) + r')\b'
        return re.search(pattern, text.lower()) is not None

    def ask_gemini(self, question):
        try:
            start_time = time.time()
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=question,
                config=self.model_config
            )
            logging.info(f"Gemini ответил за {time.time() - start_time:.2f} секунд")
            return response.text
        except ValueError as e:
            logging.error(f"Ошибка Gemini API: {e}")
            return None

    def handle_message(self, message, user_name, context=None):
        """
        Обрабатывает входящее сообщение и возвращает ответ.
        
        Args:
            message (str): Текст сообщения от пользователя
            user_name (str): Имя пользователя
            context (str, optional): Контекст из предыдущего сообщения (reply_to_message)
            
        Returns:
            str: Ответ на сообщение
        """
        if self.is_insult(message):
            return random.choice(self.config['insult_responses'])

        prompt = self.config['prompt_template'].format(user_name=user_name)
        
        # Если есть контекст, добавляем его естественным образом в промпт
        if context:
            # Убираем завершающие ": " из промпта для естественной вставки контекста
            base_prompt = prompt.rstrip(': ')
            full_question = f"{base_prompt} в ответ на твое сообщение \"{context}\": {message}"
        else:
            full_question = prompt + message
            
        response = self.ask_gemini(full_question)

        return response if response else random.choice(self.config['error_responses'])
