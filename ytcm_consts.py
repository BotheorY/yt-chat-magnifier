import os

# API credentials and configuration
YTCM_YT_TOKEN_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'ytcm_youtube_token.json'))
YTCM_GOOGLE_CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'ytcm_google_credentials.json'))
YTCM_OPENAI_CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'ytcm_openai_credentials.json'))
YTCM_POLLY_CONFIG_FILE =os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'ytcm_polly_credentials.json'))

# Logging configuration
YTCM_DEBUG_MODE = True  # Enable/disable error logging
YTCM_TRACE_MODE = True  # Enable/disable operation tracing

# Messages filtering configuration
YTCM_MIN_MESSAGE_WORDS = 3  # Minimum number of words in a message
YTCM_APPLY_MODERATION = True  # Apply moderation to messages
YTCM_QUESTIONS_ONLY = True  # Process only questions

# Messages processing configuration
YTCM_RETRIEVE_MSG_AUTHOR_GENDER = True
YTCM_APPLY_SPELLING_CORRECTION = True
YTCM_MSG_FORCED_LANG = 'Italian'   # If YTCM_APPLY_SPELLING_CORRECTION = True, force messages language (None = no translation)

# Text-To-Speech configuration (available voices: https://docs.aws.amazon.com/polly/latest/dg/available-voices.html)
YTCM_MALE_TTS_VOICE = 'Giorgio'
YTCM_FEMALE_TTS_VOICE = 'Bianca'
YTCM_TTS_AUDIO_FILES_DIR = 'static/tmp/ytcm/'  # Directory to store TTS audio files

# ChatGPT configuration
YTCM_GPT_MODEL = "gpt-4.1"  # GPT model to use

# Polling configuration
YTCM_POLLING_INTERVAL_MS = 10000  # Polling interval in milliseconds for fetching messages

YTCM_LAYOUT_STYLE = 'standard'  # Avaiable layout style: standard, dark, high-contrast