# API credentials and configuration
YTCM_YT_TOKEN_FILE = 'config/ytcm_youtube_token.json'
YTCM_GOOGLE_CONFIG_FILE = 'config/ytcm_google_credentials.json'
YTCM_OPENAI_CONFIG_FILE = 'config/ytcm_openai_credentials.json'

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

# ChatGPT configuration
YTCM_GPT_MODEL = "chatgpt-4o-latest"  # GPT model to use

# Polling configuration
YTCM_POLLING_INTERVAL_MS = 10000  # Polling interval in milliseconds for fetching messages