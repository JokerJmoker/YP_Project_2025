from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'user': os.getenv('POSTGRESS_USER'),
    'password': os.getenv('POSTGRESS_PASSWORD'),
    'host': os.getenv('POSTGRESS_HOST'),
    'port': os.getenv('POSTGRESS_PORT'),
    'database': os.getenv('POSTGRESS_DB')
}