import logging
import openai
#from openai import OpenAI as oai

logger = logging.getLogger('chat_magnifier')

class OpenAIService:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        self.model = "chatgpt-4o-latest"
    
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
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an assistant that analyzes messages to determine if they are questions. Answer only with 'YES' or 'NO'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            # Extract the response
            answer = response.choices[0].message.content.strip().upper()
            
            logger.info(f"OpenAI has determined that the message '{text}' is a question: {answer == 'YES'}")
            
            return answer == 'YES'
        
        except Exception as e:
            logger.error(f"Error during message analysis with OpenAI: {str(e)}")
            # In case of error, we assume it's not a question
            return False

    def is_appropriate(self, text):
        try:
#            client = oai(api_key = self.api_key)
            response = openai.moderations.create(
                input=text,
                model="omni-moderation-latest"
            )
            results = response.results[0]
            is_inappropriate = results.flagged
#            categories = results.categories.model_dump()
#            categories = {k: v for k, v in categories.items() if v}
#            categories = list(categories.keys())
            logger.info(f"OpenAI has determined that the message '{text}' is appropriate: {not is_inappropriate}")
            return not is_inappropriate
        except Exception as e:
            logger.error(f"Error during message moderation with OpenAI: {str(e)}")
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
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an assistant that analyzes usernames to determine if they likely belong to male users. Answer only with 'YES' or 'NO'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            # Extract the response
            answer = response.choices[0].message.content.strip().upper()
            
            logger.info(f"OpenAI has determined that the username '{username}' belongs to a male user: {answer == 'YES'}")
            
            return answer == 'YES'
        
        except Exception as e:
            logger.error(f"Error during username gender analysis with OpenAI: {str(e)}")
            # In case of error, we return False
            return False
