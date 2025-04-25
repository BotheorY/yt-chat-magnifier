import openai
import re
from ytcm_consts import *
from ytcm_utils import *

class OpenAIService:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        self.model = YTCM_GPT_MODEL
    
    def is_question(self, text):

        """
        Determines if the text is a question using OpenAI GPT-4o
        
        Args:
            text (str): The text to analyze
            
        Returns:
            bool: True if the text is a question, False otherwise
        """
        try:
            # Prepare the prompt for the API
            prompt = f"""Determine if the following message is a question. Answer only with 'YES' or 'NO'.
            
            Message: {text}
            """
            
            # Call to OpenAI API
            response = openai.chat.completions.create (
                model=self.model,
                messages=[
                    {
                    "role": "system",
                    "content": [
                        {
                        "type": "text",
                        "text": "You are an assistant that analyzes messages to determine if they are questions. Answer only with 'YES' or 'NO'."
                        }
                    ]
                    },
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": prompt
                        }
                    ]
                    }
                ],
                response_format={
                    "type": "text"
                },
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Extract the response
            answer = response.choices[0].message.content.strip().upper()
            
            info_log(f"OpenAI has determined that the message '{text}' is a question: {answer == 'YES'}")
            
            return answer == 'YES'
        
        except Exception as e:
            err_log(f"Error during message analysis with OpenAI: {str(e)}")
            # In case of error, we assume it's not a question
            return False

    def is_appropriate(self, text):
        try:
            response = openai.moderations.create(
                input=text,
                model="omni-moderation-latest"
            )
            results = response.results[0]
            is_inappropriate = results.flagged

            info_log(f"OpenAI has determined that the message '{text}' is appropriate: {not is_inappropriate}")

            return not is_inappropriate
        except Exception as e:
            err_log(f"Error during message moderation with OpenAI: {str(e)}")
            return True

    def is_male_username(self, username):
        """
        Determines if a YouTube username likely belongs to a male user using OpenAI GPT-4
        
        Args:
            username (str): The YouTube username to analyze
            
        Returns:
            bool: True if the username likely belongs to a male user, False otherwise
        """
        try:
            # Prepare the prompt for the API
            prompt = f"""Analyze the following YouTube username and determine if it likely belongs to a male user. 
            Consider common male names, masculine words, and typical male identifiers.
            Answer only with 'YES' or 'NO'.
            
            Username: {username}
            """
            
            # Call to OpenAI API
            response = openai.chat.completions.create (
                model=self.model,
                messages=[
                    {
                    "role": "system",
                    "content": [
                        {
                        "type": "text",
                        "text": "You are an assistant that analyzes usernames to determine if they likely belong to male users. Answer only with 'YES' or 'NO'."
                        }
                    ]
                    },
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": prompt
                        }
                    ]
                    }
                ],
                response_format={
                    "type": "text"
                },
                temperature=1.5,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Extract the response
            answer = response.choices[0].message.content.strip().upper()
            
            info_log(f"OpenAI has determined that the username '{username}' belongs to a male user: {answer == 'YES'}")
            
            return answer == 'YES'
        
        except Exception as e:
            err_log(f"Error during username gender analysis with OpenAI: {str(e)}")
            # In case of error, we return False
            return False
            
    def correct_text(self, text):
        """
        Corrects spelling and improves the form of a text while preserving YouTube emoticons
        
        Args:
            text (str): The text to correct
            
        Returns:
            str: The corrected text with preserved emoticons
        """
        try:
            if not text:
                return text
                
            # Identify YouTube emoticons using regex pattern
            emoticon_pattern = r':([-a-z]+):'
            emoticons = re.findall(emoticon_pattern, text)
            
            # Replace emoticons with placeholders to protect them
            protected_text = text
            placeholder_map = {}
            
            for i, emoticon in enumerate(emoticons):
                emoticon_code = f':{emoticon}:'
                placeholder = f'__EMOTICON_{i}__'
                protected_text = protected_text.replace(emoticon_code, placeholder)
                placeholder_map[placeholder] = emoticon_code
            
            # Prepare the prompt for the API
            if YTCM_MSG_FORCED_LANG:
                translation_addendum = f" \nIf the text language is different from {YTCM_MSG_FORCED_LANG}, translate the text into {YTCM_MSG_FORCED_LANG}."
            else:
                translation_addendum = ""
            prompt = f"""Correct the spelling and improve the form of the following text. 
            Maintain the original meaning and tone. Do not add or remove information.
            Do not modify any placeholders in the format __EMOTICON_X__.{translation_addendum}
            
            Text: {protected_text}
            """
            
            # Call to OpenAI API
            response = openai.chat.completions.create (
                model=self.model,
                messages=[
                    {
                    "role": "system",
                    "content": [
                        {
                        "type": "text",
                        "text": "You are an assistant that corrects spelling and improves text form while preserving special placeholders."
                        }
                    ]
                    },
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": prompt
                        }
                    ]
                    }
                ],
                response_format={
                    "type": "text"
                },
                temperature=0.3,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Extract the corrected text
            corrected_text = response.choices[0].message.content.strip()
            
            # Restore emoticons from placeholders
            for placeholder, emoticon_code in placeholder_map.items():
                corrected_text = corrected_text.replace(placeholder, emoticon_code)
            
            info_log(f"OpenAI has corrected the text: '{text}' to '{corrected_text}'")
            
            return corrected_text
        
        except Exception as e:
            err_log(f"Error during text correction with OpenAI: {str(e)}")
            # In case of error, return the original text
            return text
