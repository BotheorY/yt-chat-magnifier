# YouTube Chat Magnifier

A Flask web application that reads YouTube livestream chat in real-time and allows viewing, filtering, reading, and/or listening to messages in a way that is accessible to visually impaired people.

## Features

- Connection to YouTube APIs to read chat in real-time
- Display of messages in a real-time updated list
- Manually removing messages from the list
- Showing only messages with questions and/or containing a minimum number of words
- Automatic exclusion of messages from list through AI moderation
- Zoom on message text by increasing text size
- Voice playback of messages via text-to-speech (through AWS Polly API)
- Responsive interface with Bootstrap

## Requirements

- Python 3.7+
- Flask
- Google API Client
- OpenAI API

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure credentials:
   - Insert your Google API credentials in `config/ytcm_google_credentials.json`
   - Insert your OpenAI token in `config/ytcm_openai_credentials.json`

## Usage

1. Start the application:

```bash
python app.py
```

2. Open your browser at `http://localhost:5000`
3. Click on the "CONNECT TO YOUTUBE" button to start monitoring the chat
4. Filtered messages will be displayed in the list

## Project Structure

- `app.py`: Main Flask application file
- `ytcm_youtube_chat_reader.py`: Module for connecting to YouTube APIs
- `ytcm_openai_service.py`: Module for OpenAI integration
- `templates/`: Folder containing HTML templates
- `config/`: Folder containing configuration files
- `logs/`: Folder containing log files

## Logging Configuration

The application uses a configurable logging system:

- `YTCM_DEBUG_MODE`: Enable/disable error logging
- `YTCM_TRACE_MODE`: Enable/disable operation tracing

Logs are saved in the `logs/` folder.