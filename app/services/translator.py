import os
import requests
import uuid
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MicrosoftTranslator:
    def __init__(self):
        self.key = os.getenv('MS_TRANSLATOR_KEY')
        self.endpoint = "https://api.cognitive.microsofttranslator.com"
        self.location = os.getenv('MS_TRANSLATOR_LOCATION', 'global')
        
        # Log initialization status
        logger.info(f"Translator initialized with endpoint: {self.endpoint}")
        logger.info(f"Location: {self.location}")
        logger.info(f"API Key present: {'Yes' if self.key else 'No'}")

    def translate(self, text: str, from_lang: str = 'zh', to_lang: str = 'en') -> Optional[str]:
        if not self.key:
            logger.error("Microsoft Translator API key not found in environment variables")
            raise ValueError("Microsoft Translator API key not found in environment variables")

        # Ensure the text is properly encoded as UTF-8
        try:
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            
            # Normalize unicode characters
            text = text.encode('utf-8').decode('utf-8')
            
            # Remove any null characters that might cause issues
            text = text.replace('\x00', '')
            
        except Exception as e:
            logger.error(f"Text encoding error: {e}")
            return None

        path = '/translate'
        constructed_url = self.endpoint + path

        params = {
            'api-version': '3.0',
            'from': from_lang,
            'to': to_lang
        }

        headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Ocp-Apim-Subscription-Region': self.location,
            'Content-type': 'application/json; charset=utf-8',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        body = [{
            'text': text
        }]

        try:
            logger.info(f"Attempting to translate text: {text[:50]}...")  # Log first 50 chars of text
            
            # Ensure JSON is properly encoded
            response = requests.post(
                constructed_url, 
                params=params, 
                headers=headers, 
                json=body,
                timeout=30
            )
            
            # Log response status and headers
            logger.info(f"Translation API Response Status: {response.status_code}")
            logger.info(f"Response Headers: {response.headers}")
            
            if response.status_code != 200:
                logger.error(f"Translation API Error. Status Code: {response.status_code}")
                logger.error(f"Response Content: {response.text}")
                return None

            response.raise_for_status()
            
            # Ensure response is properly decoded
            response.encoding = 'utf-8'
            result = response.json()
            
            logger.info(f"Translation API Response: {result}")
            
            if result and len(result) > 0:
                translations = result[0].get('translations', [])
                if translations and len(translations) > 0:
                    translated_text = translations[0].get('text')
                    
                    # Ensure translated text is properly encoded
                    if translated_text:
                        try:
                            translated_text = translated_text.encode('utf-8').decode('utf-8')
                        except Exception as e:
                            logger.warning(f"Translation text encoding warning: {e}")
                    
                    logger.info(f"Successfully translated to: {translated_text}")
                    return translated_text
            logger.warning("No translation found in the response")
            return None
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            logger.error(f"Full error details: ", exc_info=True)
            return None