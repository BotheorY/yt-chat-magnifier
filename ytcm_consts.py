import os

# API credentials and configuration
YTCM_YT_TOKEN_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'ytcm_youtube_token.json'))
YTCM_GOOGLE_CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'ytcm_google_credentials.json'))
YTCM_OPENAI_CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'ytcm_openai_credentials.json'))
YTCM_OPENAI_BASE_URL = None
YTCM_GPT_MODEL = "gpt-4.1"  # GPT model to use
YTCM_POLLY_CONFIG_FILE =os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'ytcm_polly_credentials.json'))

# Logging configuration
YTCM_DEBUG_MODE = True  # Enable/disable error logging
YTCM_TRACE_MODE = True  # Enable/disable operation tracing
YTCM_LOGGER_NAME = 'yt_chat_magnifier'  # Logger name
YTCM_LOG_FILE_DIR = 'logs'  # Directory to store log files
YTCM_LOG_FILE_NAME = 'yt-chat-magnifier.log'  # Log file name
YTCM_LOG_FILE_MAX_SIZE = 10485760  # Maximum log file size in bytes (10MB)
YTCM_LOG_FILE_BACKUP_COUNT = 10  # Number of log file backups to keep
YTCM_ERR_LOG_EXTRA_INFO = None  # Include extra information in error logs

# Messages filtering configuration
YTCM_IGNORE_CHANNEL_OWNER_MESSAGES = True  # Ignore messages from channel owner
YTCM_MIN_MESSAGE_WORDS = 2  # Minimum number of words in a message
YTCM_APPLY_MODERATION = True  # Apply moderation to messages
YTCM_QUESTIONS_ONLY = True  # Process only questions

# Messages processing configuration
YTCM_RETRIEVE_MSG_AUTHOR_GENDER = True
YTCM_APPLY_SPELLING_CORRECTION = True
YTCM_MSG_FORCED_LANG = 'Italian'   # If YTCM_APPLY_SPELLING_CORRECTION = True, force messages language (None = no translation)
YTCM_FORCE_MSG_UPPERCASE = True

# Text-To-Speech configuration (available voices: https://docs.aws.amazon.com/polly/latest/dg/available-voices.html)
YTCM_MALE_TTS_VOICE = 'Giorgio'
YTCM_FEMALE_TTS_VOICE = 'Bianca'
YTCM_TTS_AUDIO_FILES_DIR = 'static/tmp/ytcm/'  # Directory to store TTS audio files

# Polling configuration
YTCM_POLLING_INTERVAL_MS = 10000  # Polling interval in milliseconds for fetching messages

YTCM_LAYOUT_STYLE = 'dark'  # Avaiable layout style: standard, dark, high-contrast