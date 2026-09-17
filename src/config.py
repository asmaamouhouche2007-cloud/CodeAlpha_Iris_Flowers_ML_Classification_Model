from dotenv import load_dotenv
import os 

load_dotenv()

SECRET_KEY=os.environ.get('SECRET_KEY')
DB_NAME=os.environ.get('DB_NAME','model_feedback.db')
# configuration file