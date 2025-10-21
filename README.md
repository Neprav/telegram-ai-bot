# AI-Powered Telegram Bot

A configurable Telegram bot powered by Google Gemini AI that responds to user messages with customizable personality and behavior patterns.

## Overview

This is a flexible Telegram bot framework that can be configured with any personality or purpose. It uses Google's Gemini 2.5 Flash model to generate intelligent, context-aware responses. The bot includes configurable trigger words, insult detection, error handling, and custom personality prompts.

## Quick Start

**Setup:**
1. Clone this repository
2. Copy `env.template` to `.env` and add your API credentials
3. Copy `config.json.example` to `config.json` and customize it
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python main.py`

## Features

- **AI-Powered Responses**: Uses Google Gemini 2.5 Flash for natural language understanding and generation
- **Fully Customizable Personality**: Configure bot behavior through JSON configuration file
- **Configurable Trigger Word**: Activate bot with any custom trigger word
- **Insult Detection**: Detects offensive language and responds with pre-configured messages
- **Flexible Deployment**: Supports both local development and Google Cloud Run deployment
- **Cloud Configuration**: Can load configuration from Google Cloud Storage
- **GUI Test Client**: Includes a Tkinter-based testing interface for local development
- **Webhook Integration**: Receives messages from Telegram via webhook API

## Technical Architecture

### Core Components

#### 1. Main Application (`main.py`)

The Flask-based web server that handles Telegram webhook requests.

**Key Features:**
- **Dual Configuration Loading**: Automatically detects environment (Cloud Run vs. local) and loads configuration accordingly
  - Cloud Run: Loads `config.json` from Google Cloud Storage
  - Local: Loads from local file system with `.env` support
- **Webhook Endpoint**: `/webhook` POST endpoint for receiving Telegram updates
- **Message Processing**: Filters messages starting with configured trigger word and passes them to the handler
- **Response Delivery**: Sends bot responses back to Telegram using the Bot API

**Environment Variables Required:**
- `TELEGRAM_TOKEN`: Telegram Bot API token
- `GEMINI_API_KEY`: Google Gemini API key
- `GCS_BUCKET_NAME`: (Cloud Run only) Google Cloud Storage bucket name

#### 2. Message Handler (`message_handler.py`)

Contains the core business logic for processing and generating responses.

**Class: `MessageHandler`**

**Initialization:**
```python
def __init__(self, config):
    self.config = config
    self.client = genai.Client(api_key=api_key)
    self.model_config = {
        "temperature": 1.4,      # High creativity
        "top_p": 0.99,          # Nucleus sampling threshold
        "top_k": 0,             # Disabled (use top_p only)
        "max_output_tokens": 4096
    }
```

**Key Methods:**

- `is_insult(text)`: Uses regex pattern matching to detect offensive words from configured word list
- `ask_gemini(question)`: Sends requests to Gemini API with configured parameters and logs response time
- `handle_message(message, user_name)`: Main entry point that:
  1. Checks for insults → returns random insult response
  2. Builds prompt with personality template + user name
  3. Calls Gemini API
  4. Returns response or error message on failure

**AI Model Configuration:**
- Model: `gemini-2.5-flash`
- Temperature: 1.4 (high creativity/randomness)
- Max tokens: 4096
- Top-p sampling: 0.99

#### 3. Configuration (`config.json`)

JSON-based configuration file that defines bot behavior. Copy from `config.json.example` and customize:

**Configuration Structure:**

```json
{
    "trigger_word": "botname",
    "insults": [
        "stupid", "idiot", "dumb", "fool", "moron"
    ],
    "insult_responses": [
        "Hey, let's keep it civil!",
        "No need for that kind of language",
        "That's not very nice",
        "Let's have a normal conversation",
        "Come on, be respectful"
    ],
    "error_responses": [
        "Sorry, I don't understand that",
        "I'm not sure what you mean",
        "Could you rephrase that?",
        "I can't answer that question",
        "That's beyond my capabilities"
    ],
    "prompt_template": "You are a Telegram bot with a specific personality. Respond in a conversational style. Keep responses under 50 words. User {user_name} asks: "
}
```

**Configuration Parameters:**

- **`trigger_word`** (string): The word that activates the bot (e.g., "botname", "assistant", "help")
- **`insults`** (array): List of offensive words to detect and filter
- **`insult_responses`** (array): Pre-defined responses when insults are detected
- **`error_responses`** (array): Fallback responses when AI fails to generate a response
- **`prompt_template`** (string): System prompt that defines bot personality and behavior
  - Use `{user_name}` placeholder to include the user's first name in the prompt

**Customization:**

Modify the `prompt_template` to define your bot's:
- Personality traits and tone
- Expertise areas and knowledge domain
- Response length and format preferences
- Behavioral guidelines and restrictions
- Language and communication style

#### 4. GUI Test Client (`simple_gui_client.py`)

Tkinter-based desktop application for local testing without Telegram integration.

**Features:**
- Multi-line text input
- Send button and Enter key support
- Shift+Enter for newlines
- Clear button for input reset
- Response display area with word wrapping
- Dynamically loads configuration on each message

**Usage:** Ideal for testing message handling logic and bot responses during development.

### Deployment Architecture

#### Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` file with required environment variables
3. Create `config.json` from `config.json.example` and customize it
4. Run with: `python main.py`
5. Use ngrok or similar for webhook testing

#### Docker Deployment

The included `Dockerfile` creates a production-ready container:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["gunicorn", "-w", "1", "-k", "gevent", "-b", "0.0.0.0:8080", "--timeout", "60", "main:app"]
```

**Container Configuration:**
- Base: Python 3.10 slim
- Server: Gunicorn with Gevent worker
- Workers: 1 (single worker for async handling)
- Port: 8080
- Timeout: 60 seconds

**Build and Run:**
```bash
docker build -t telegram-bot .
docker run -p 8080:8080 \
  -e TELEGRAM_TOKEN=<token> \
  -e GEMINI_API_KEY=<key> \
  telegram-bot
```

#### Google Cloud Run Deployment

The bot is designed for serverless deployment on Cloud Run:

1. **Configuration Storage**: `config.json` stored in Google Cloud Storage bucket
2. **Environment Detection**: Checks for `K_SERVICE` environment variable
3. **Automatic Scaling**: Cloud Run handles traffic scaling
4. **Secret Management**: API keys stored in environment variables

**Deployment Steps:**

1. Upload `config.json` to Google Cloud Storage:
```bash
gsutil cp config.json gs://your-bucket-name/config.json
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy telegram-bot \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_TOKEN=<token>,GEMINI_API_KEY=<key>,GCS_BUCKET_NAME=<bucket>
```

### API Integrations

#### Telegram Bot API

- **Webhook Mode**: Receives updates via POST to `/webhook`
- **Message Sending**: Uses `sendMessage` method with reply functionality
- **Activation Pattern**: Messages starting with `"{trigger_word} "` or `"{trigger_word},"`
- **Timeout**: 10 seconds for API requests

#### Google Gemini API

- **Client**: Uses `google-genai` Python SDK
- **Model**: gemini-2.5-flash
- **Request Format**: Combined prompt template + user message
- **Error Handling**: Catches `ValueError` exceptions and logs errors
- **Performance Monitoring**: Logs response time for each request

#### Google Cloud Storage

- **Usage**: Stores and retrieves `config.json` in cloud deployments
- **Client**: `google-cloud-storage` library
- **Authentication**: Uses default application credentials in Cloud Run
- **Encoding**: UTF-8 text encoding

## Dependencies

Core dependencies from `requirements.txt`:

```
flask>=2.3.3                    # Web framework
requests>=2.31.0                # HTTP client for Telegram API
gunicorn>=21.2.0                # Production WSGI server
gevent>=22.10.2                 # Async worker for Gunicorn
google-cloud-storage>=2.14.0    # GCS integration
google-genai                    # Gemini AI SDK
python-dotenv>=1.0.0            # Environment variable management
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_TOKEN` | Yes | Bot token from @BotFather |
| `GEMINI_API_KEY` | Yes | Google AI Studio API key |
| `GCS_BUCKET_NAME` | Cloud Run | GCS bucket name for config |
| `PORT` | Optional | Server port (default: 8080) |
| `K_SERVICE` | Auto | Cloud Run service indicator |

## Project Structure

```
telegram-bot/
├── main.py                      # Flask application & webhook handler
├── message_handler.py           # AI integration & response logic
├── simple_gui_client.py         # Local testing GUI
├── config.json.example          # Example configuration template
├── env.template                 # Environment variables template
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container configuration
├── README.md                    # This file
└── venv/                        # Virtual environment (gitignored)
```

**Important:** Create these files before running:
- `config.json` - Copy from `config.json.example` and customize
- `.env` - Add your API keys and tokens

## Usage

### 1. Get Required API Credentials

**Telegram Bot Token:**
1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow the instructions
3. Copy the API token provided

**Google Gemini API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 2. Configure the Bot

1. Copy `config.json.example` to `config.json`:
```bash
cp config.json.example config.json
```

2. Edit `config.json` and customize:
   - `trigger_word`: Choose your bot's activation word
   - `prompt_template`: Define your bot's personality and behavior
   - `insults`, `insult_responses`, `error_responses`: Adjust as needed

3. Copy `env.template` to `.env`:
```bash
cp env.template .env
```

4. Add your credentials to `.env`:
```
TELEGRAM_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Set Up Telegram Webhook

After deploying the bot (locally with ngrok or to Cloud Run), set the webhook URL:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-bot-url.com/webhook"}'
```

### 4. Interact with the Bot

In any Telegram chat where the bot is present, use your configured trigger word:

```
User: botname, what's the weather like?
Bot: [AI-generated response based on your prompt_template]

User: botname tell me a joke
Bot: [AI-generated response based on your prompt_template]
```

**Note:** Replace "botname" with whatever you configured as `trigger_word` in `config.json`.

### 5. Local Testing

Run the GUI client for local testing without Telegram:

```bash
python simple_gui_client.py
```

This allows you to test your bot's responses and configuration before deploying.

## Logging

The application uses Python's logging module with INFO level:
- Logs output to stdout
- Format: `%(asctime)s [%(levelname)s] %(message)s`
- Tracks Gemini API response times
- Logs errors for failed API calls and configuration loading

## Security Considerations

1. **API Keys**: Never commit `.env`, `config.json`, or expose tokens in code
2. **Git Ignore**: Ensure sensitive files are in `.gitignore`
3. **Environment Variables**: Use Cloud Run secrets or environment variables for production
4. **Rate Limiting**: Consider implementing rate limits for API calls
5. **Input Validation**: Message text is stripped and lowercased before processing
6. **Timeout Protection**: 10-second timeout on Telegram API calls, 60-second server timeout

## Customization

### Modifying Bot Personality

Edit `config.json`:

- **Change trigger word**: Update `trigger_word` to any word you want (e.g., "help", "assistant", "bot")
- **Define personality**: Modify `prompt_template` to create any character or expert persona
- **Adjust filters**: Update `insults` array to match your use case
- **Customize responses**: Modify `insult_responses` and `error_responses`

**Example Personalities:**

Customer Support Bot:
```json
"prompt_template": "You are a helpful customer support assistant. Be professional, empathetic, and solution-focused. Keep responses under 100 words. Customer {user_name} asks: "
```

Coding Assistant:
```json
"prompt_template": "You are an expert software developer. Provide clear, concise technical answers with code examples when relevant. Keep responses under 200 words. Developer {user_name} asks: "
```

Teacher Bot:
```json
"prompt_template": "You are a patient and encouraging teacher. Explain concepts clearly and provide examples. Keep responses educational and under 100 words. Student {user_name} asks: "
```

### Adjusting AI Parameters

In `message_handler.py`, modify `model_config`:

```python
self.model_config = {
    "temperature": 1.4,          # 0.0-2.0 (lower=focused, higher=creative)
    "top_p": 0.99,              # 0.0-1.0 (nucleus sampling)
    "max_output_tokens": 4096   # Maximum response length
}
```

- **Lower temperature (0.3-0.7)**: More consistent, factual responses
- **Higher temperature (1.0-1.5)**: More creative, varied responses
- **Very high temperature (1.5-2.0)**: Very unpredictable, experimental

### Changing Activation Trigger

The bot currently activates on messages starting with the configured trigger word followed by space or comma. To modify this behavior, edit `main.py`:

```python
if text.startswith((f"{TRIGGER_WORD} ", f"{TRIGGER_WORD},")):
    # Process message
```

## Troubleshooting

**Bot not responding:**
- Check webhook is properly set with `/getWebhookInfo`
- Verify `TELEGRAM_TOKEN` is correct in `.env`
- Ensure bot has access to chat messages (privacy mode settings)
- Check logs for errors

**Gemini API errors:**
- Confirm `GEMINI_API_KEY` is valid
- Check API quota and billing in Google Cloud Console
- Review logs for specific error messages
- Verify network connectivity

**Configuration not loading:**
- Verify `config.json` exists and is valid JSON (use a JSON validator)
- Check file encoding is UTF-8
- In Cloud Run: verify GCS bucket permissions and `GCS_BUCKET_NAME`
- Check logs for specific loading errors

**Local testing issues:**
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check `.env` file exists and has correct format
- Use GUI client to test without Telegram integration

## Example Use Cases

This bot framework can be configured for various purposes:

1. **Customer Support**: Handle FAQs and support queries
2. **Educational Assistant**: Help students with homework and explanations
3. **Team Productivity**: Provide information and automate team tasks
4. **Personal Assistant**: Schedule reminders and answer questions
5. **Community Moderator**: Answer common questions in group chats
6. **Entertainment**: Create character-based chatbots for fun

## Future Enhancements

Potential improvements and features:

- Add conversation history/context management
- Implement user-specific settings and preferences
- Add multi-language support
- Create admin commands for runtime configuration
- Add analytics and usage statistics
- Implement caching for frequent queries
- Add support for images and media
- Create command-based interactions
- Add database integration for persistent storage

## License

This project is available for personal and educational use.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

If you encounter issues or have questions:

- 🐛 **Report bugs**: Open an issue on GitHub
- 💡 **Suggest features**: Create a feature request
- 📖 **Documentation**: Check this README and code comments
- ⭐ **Star the repo**: If you find this useful!

---

**Note:** This bot uses AI-generated responses. Configure your `config.json` appropriately for your use case and audience. Always review and test bot behavior before deploying to production.

