# Gena Telegram Bot

A personality-driven Telegram bot powered by Google Gemini AI that responds to user messages with a unique character - a cynical, informal beer expert and philosopher named Gena.

## Overview

Gena is a Telegram bot that activates when users mention his name in chat. He provides witty, informal responses using Google's Gemini 2.5 Flash model with custom personality prompts. The bot includes profanity filtering, insult detection, and character-appropriate responses.

## Quick Start

**Setup:**
1. Clone repository
2. Copy `env.template` to `.env` and fill in your credentials
3. Copy `config.json.example` to `config.json`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python main.py`

## Features

- **AI-Powered Responses**: Uses Google Gemini 2.5 Flash for natural language understanding and generation
- **Custom Personality**: Cynical, informal character with configurable behavior patterns
- **Insult Detection**: Detects offensive language and responds with pre-configured witty comebacks
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
- **Message Processing**: Filters messages starting with "гена " or "гена," and passes them to the handler
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

- `is_insult(text)`: Uses regex pattern matching to detect profanity from configured word list
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

JSON-based configuration file containing:

**Sections:**
- `insults`: Array of profanity/offensive words for detection (18 words)
- `insult_responses`: Array of 11 witty comeback responses
- `error_responses`: Array of 5 error handling responses
- `prompt_template`: System prompt that defines bot personality

**Prompt Template Details:**
The prompt instructs the AI to:
- Act as "Gena" created by Kirill
- Adopt a cynical, informal personality
- Be a beer expert and philosopher
- Use conversational, informal language
- Be more polite to female users
- Keep responses under 50 words
- Avoid using '*' for formatting
- Respond with "Хз" if uncertain

#### 4. GUI Test Client (`simple_gui_client.py`)

Tkinter-based desktop application for local testing without Telegram integration.

**Features:**
- Multi-line text input
- Send button and Enter key support
- Shift+Enter for newlines
- Clear button for input reset
- Response display area with word wrapping
- Loads configuration dynamically on each message

**Usage:** Ideal for testing message handling logic and bot responses during development.

### Deployment Architecture

#### Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` file with required environment variables
3. Place `config.json` in project root
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

#### Google Cloud Run Deployment

The bot is designed for serverless deployment on Cloud Run:

1. **Configuration Storage**: `config.json` stored in Google Cloud Storage bucket
2. **Environment Detection**: Checks for `K_SERVICE` environment variable
3. **Automatic Scaling**: Cloud Run handles traffic scaling
4. **Secret Management**: API keys stored in environment variables

**Deployment Command:**
```bash
gcloud run deploy gena-bot \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_TOKEN=<token>,GEMINI_API_KEY=<key>,GCS_BUCKET_NAME=<bucket>
```

### API Integrations

#### Telegram Bot API

- **Webhook Mode**: Receives updates via POST to `/webhook`
- **Message Sending**: Uses `sendMessage` method with reply functionality
- **Activation Trigger**: Messages starting with "гена " or "гена,"
- **Timeout**: 10 seconds for API requests

#### Google Gemini API

- **Client**: Uses `google-genai` Python SDK
- **Model**: gemini-2.5-flash
- **Request Format**: Simple content string with combined prompt + question
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
Gena New/
├── main.py                      # Flask application & webhook handler
├── message_handler.py           # AI integration & response logic
├── simple_gui_client.py         # Local testing GUI
├── config.json.example          # Example bot configuration (copy to config.json)
├── env.template                 # Environment variables template (copy to .env)
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container configuration
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
└── venv/                        # Virtual environment (gitignored)
```

**Note:** Files excluded from Git:
- `config.json` - Create from `config.json.example`
- `.env` - Create with your API keys
- `*.bat` - Windows batch scripts for local development
- `venv/` - Virtual environment
- `__pycache__/` - Python cache files

## Usage

### Setting Up Telegram Webhook

After deploying the bot, set the webhook URL:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-cloud-run-url.run.app/webhook"}'
```

### Interacting with the Bot

In any Telegram chat where the bot is present:

```
User: гена, what's the best beer?
Bot: [Cynical, informal response about beer]

User: гена какая погода?
Bot: [Response in bot's characteristic style]
```

### Testing Locally

1. Run the GUI client:
   ```bash
   python simple_gui_client.py
   ```
   Or on Windows: `run_simple_gui_client.py.bat`

2. Enter messages and test responses without Telegram integration

## Logging

The application uses Python's logging module with INFO level:
- Logs are output to stdout
- Format: `%(asctime)s [%(levelname)s] %(message)s`
- Tracks Gemini API response times
- Logs errors for failed API calls and configuration loading

## Security Considerations

1. **API Keys**: Never commit `.env` or expose tokens in code
2. **Environment Variables**: Use Cloud Run secrets for production
3. **Rate Limiting**: Consider implementing rate limits for API calls
4. **Input Validation**: Message text is stripped and lowercased
5. **Timeout Protection**: 10-second timeout on Telegram API calls, 60-second on server

## Customization

### Modifying Bot Personality

Edit `config.json`:
- Update `prompt_template` to change character behavior
- Modify `insults` array to adjust profanity detection
- Customize `insult_responses` and `error_responses`

### Adjusting AI Parameters

In `message_handler.py`, modify `model_config`:
- `temperature`: 0.0-2.0 (lower = more focused, higher = more creative)
- `top_p`: 0.0-1.0 (nucleus sampling threshold)
- `max_output_tokens`: Maximum response length

### Changing Activation Trigger

In `main.py`, update the activation condition:
```python
if text.startswith(("гена ", "гена,")):  # Modify these triggers
```

## Troubleshooting

**Bot not responding:**
- Check webhook is properly set
- Verify `TELEGRAM_TOKEN` is correct
- Ensure bot has access to chat messages

**Gemini API errors:**
- Confirm `GEMINI_API_KEY` is valid
- Check API quota and billing
- Review logs for specific error messages

**Configuration not loading:**
- Verify `config.json` exists and is valid JSON
- Check GCS bucket permissions in Cloud Run
- Ensure `GCS_BUCKET_NAME` is set correctly

## Future Enhancements

- Add conversation history/context management
- Implement user-specific settings
- Add multi-language support
- Create admin commands for runtime configuration
- Add analytics and usage statistics
- Implement caching for frequent queries

## License

This project is created by Kirill for personal/educational use.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Author

Created by Kirill

## Support

If you find this project useful, please consider:
- ⭐ Starring this repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing code

---

**Note:** This bot includes mature language and informal communication style. Configure `config.json` appropriately for your use case.

