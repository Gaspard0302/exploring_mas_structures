from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Access your API keys
openai_api_key = os.getenv('OPENAI_API_KEY')
