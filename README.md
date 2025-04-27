# YouTube Chat Magnifier

A Flask web application that reads YouTube livestream chat in real-time and allows viewing, filtering, reading, and/or listening to messages in a way that is accessible to visually impaired people. This tool enhances the livestream experience by making chat more accessible and manageable.

## Features

- **Real-time Chat Monitoring**: Connection to YouTube APIs to read chat in real-time from any livestream
- **Interactive Message Display**: Messages shown in a real-time updated list with auto-scrolling
- **Message Management**: Manually remove messages from the list
- **Smart Filtering**: Show only messages with questions and/or containing a minimum number of words, hide duplicates and channel owner filtering (option to ignore messages from the YouTube channel owner)
- **AI Moderation**: Automatic exclusion of offensive content through AI moderation
- **Accessibility Features**:
  - Zoom on message text by increasing text size
  - High contrast mode for better visibility
  - Voice playback of messages via text-to-speech (through AWS Polly API, voice selection according to message author gender)
  - Optional uppercase formatting for better visibility of author names and message text
  - Easy message text copying to clipboard
- **Language Features**:
  - Automatic spelling correction
  - Automatic translation to choosen language
- **Responsive Design**: Fully responsive interface with Bootstrap for desktop and mobile use
- **Theme Options**: Light, dark, and high-contrast themes available
- **Comprehensive Logging System**:
  - Configurable debug mode for detailed error tracking
  - Operation tracing for monitoring application flow
  - Rotating log files with size management

## Requirements

- Python 3.7+
- Flask 2.0+
- Google API Client
- OpenAI API or compatible alternative APIs (for AI moderation, questions recognition and message author gender detection)
- AWS Account (for Polly text-to-speech service)
- Modern web browser (Chrome, Firefox, Edge, Safari)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/BotheorY/yt-chat-magnifier.git
   cd yt-chat-magnifier
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure credentials:
   - Create a Google API project and enable YouTube Data API v3
   - Create an OpenAI account and generate an API key
   - Set up an AWS account and configure Polly access
   - Copy the example credential files and insert your keys:
     ```bash
     cp config/ytcm_google_credentials.json.example config/ytcm_google_credentials.json
     cp config/ytcm_openai_credentials.json.example config/ytcm_openai_credentials.json
     cp config/ytcm_polly_credentials.json.example config/ytcm_polly_credentials.json
     ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser at `http://localhost:5000`

3. Click on the "CONNECT TO YOUTUBE" button to start monitoring the chat

4. Configure filters and display options according to your preferences:
   - Set minimum word count for messages
   - Enable/disable question detection
   - Enable/disable channel owner message filtering
   - Enable/disable spelling correction
   - Enable/disable translation to a chosen language
   - Enable/disable AI moderation
   - Toggle text-to-speech functionality

5. Filtered messages will be displayed in the list. Double click or double tap on message to copy it to clipboard. Click or tap a message to open the zoom window and read aloud through the player if text-to-speech is enabled.

## Project Structure

- `app.py`: Main Flask application file with routes and server configuration
- `ytcm_youtube_chat_reader.py`: Module for connecting to YouTube APIs and retrieving chat messages
- `ytcm_openai_service.py`: Module for OpenAI integration and AI-based message moderation
- `ytcm_polly_service.py`: Module for AWS Polly text-to-speech integration
- `ytcm_consts.py`: Constants and configuration values used throughout the application
- `templates/`: Folder containing HTML templates for the web interface
- `static/`: Folder containing static assets:
  - `css/`: Stylesheets for different themes and components
  - `js/`: JavaScript files for client-side functionality
  - `images/`: Icons, logos, and other image assets
- `config/`: Folder containing configuration files and API credentials
- `logs/`: Folder containing application log files

## Configuration Options

The application can be configured by editing the constants in ytcm_consts.py file:

### General Configuration
- `YTCM_LAYOUT_STYLE`: UI theme ('standard', 'dark', or 'high-contrast')

### Logging Configuration
- `YTCM_DEBUG_MODE`: Enable/disable error logging (true/false)
- `YTCM_TRACE_MODE`: Enable/disable operation tracing (true/false)
- `YTCM_LOG_FILE_MAX_SIZE`: Maximum log file size in bytes (default: 10MB)
- `YTCM_LOG_FILE_BACKUP_COUNT`: Number of log file backups to keep

### Message Filtering Configuration
- `YTCM_IGNORE_CHANNEL_OWNER_MESSAGES`: Ignore messages from the channel owner (True/False)
- `YTCM_MIN_MESSAGE_WORDS`: Minimum number of words for a message to be displayed
- `YTCM_APPLY_MODERATION`: Enable/disable AI-based message moderation
- `YTCM_QUESTIONS_ONLY`: Show only messages that contain questions

### Message Processing Configuration
- `YTCM_RETRIEVE_MSG_AUTHOR_GENDER`: Detect message author gender for TTS voice selection
- `YTCM_APPLY_SPELLING_CORRECTION`: Enable/disable automatic spelling correction
- `YTCM_MSG_FORCED_LANG`: Force translation to a specific language (e.g., 'Italian', or None for no translation)
- `YTCM_FORCE_MSG_UPPERCASE`: Enable/disable uppercase formatting for author names and message text in the chat list

### Text-to-Speech Configuration
- `YTCM_MALE_TTS_VOICE`: AWS Polly voice for male authors (e.g., 'Giorgio')
- `YTCM_FEMALE_TTS_VOICE`: AWS Polly voice for female authors (e.g., 'Bianca')
- `YTCM_TTS_AUDIO_FILES_DIR`: Directory to store TTS audio files

### API Configuration
- `YTCM_GPT_MODEL`: OpenAI GPT model to use (e.g., 'gpt-4.1')
- `YTCM_OPENAI_BASE_URL`: Base URL for OpenAI API or compatible alternative LLM providers (with alternative LLM providers, AI moderation probably won't work)
- `YTCM_POLLING_INTERVAL_MS`: Polling interval in milliseconds for fetching new chat messages

## Logging Configuration

The application uses a configurable logging system:

- `YTCM_DEBUG_MODE`: Enable/disable error logging
- `YTCM_TRACE_MODE`: Enable/disable operation tracing

Logs are saved in the `logs/` folder.

## Troubleshooting

- **API Connection Issues**: Ensure your API credentials are correctly configured and have the necessary permissions
- **Message Filtering Not Working**: Check the OpenAI API quota and connection status
- **Text-to-Speech Not Working**: Verify AWS Polly credentials and network connectivity
- **Application Not Starting**: Check the logs for detailed error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.