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
            raise ValueError("GEMINI_API_KEY is not set! Check environment variables.")
        
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
            logging.info(f"Gemini responded in {time.time() - start_time:.2f} seconds")
            return response.text
        except ValueError as e:
            logging.error(f"Gemini API error: {e}")
            return None

    def handle_message(self, message, user_name, context=None):
        """
        Processes incoming message and returns a response.
        
        Args:
            message (str): Message text from user
            user_name (str): User name
            context (str, optional): Context from previous message (reply_to_message)
            
        Returns:
            str: Response to the message
        """
        if self.is_insult(message):
            return random.choice(self.config['insult_responses'])

        prompt = self.config['prompt_template'].format(user_name=user_name)
        
        # If there is context, add it naturally to the prompt
        if context:
            # Remove trailing ": " from prompt for natural context insertion
            base_prompt = prompt.rstrip(': ')
            full_question = f"{base_prompt} in response to your message \"{context}\": {message}"
        else:
            full_question = prompt + message
            
        response = self.ask_gemini(full_question)

        return response if response else random.choice(self.config['error_responses'])
