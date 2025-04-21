# YouTube Chat Magnifier

A Flask web application that reads YouTube livestream chat in real-time and allows viewing, filtering, reading, and/or listening to messages in a way that is accessible to visually impaired people. This tool enhances the livestream experience by making chat more accessible and manageable.

## Features

- **Real-time Chat Monitoring**: Connection to YouTube APIs to read chat in real-time from any livestream
- **Interactive Message Display**: Messages shown in a real-time updated list with auto-scrolling
- **Message Management**: Manually remove messages from the list
- **Smart Filtering**: Show only messages with questions and/or containing a minimum number of words, hide duplicates
- **AI Moderation**: Automatic exclusion of spam, offensive content, or irrelevant messages through AI moderation
- **Accessibility Features**:
  - Zoom on message text by increasing text size
  - High contrast mode for better visibility
  - Voice playback of messages via text-to-speech (through AWS Polly API, voice selection according to message author gender)
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
- OpenAI API (for AI moderation, questions and message author gender detection)
- AWS Account (for Polly text-to-speech service)
- Modern web browser (Chrome, Firefox, Edge, Safari)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/youtube-chat-magnifier.git
   cd youtube-chat-magnifier
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

3. Enter a YouTube livestream URL or ID in the input field

4. Click on the "CONNECT TO YOUTUBE" button to start monitoring the chat

5. Configure filters and display options according to your preferences:
   - Set minimum word count for messages
   - Enable/disable question detection
   - Enable/disable spelling correction
   - Enable/disable translation to a chosen language
   - Enable/disable AI moderation
   - Toggle text-to-speech functionality

6. Filtered messages will be displayed in the list. Double click or double tap on message to copy it to clipboard. Click or tap a message to open the zoom window and read aloud through the player if text-to-speech is enabled.

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

The application can be configured through environment variables and/or by editing the the costants in ytcm_consts.py file:

- `FLASK_ENV`: Set to `development` for debug mode or `production` for production mode
- `FLASK_PORT`: Change the default port (5000) if needed
- `YTCM_DEBUG_MODE`: Enable/disable error logging (true/false)
- `YTCM_TRACE_MODE`: Enable/disable operation tracing (true/false)
- `YTCM_TTS_ENABLED`: Enable/disable text-to-speech functionality by default

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