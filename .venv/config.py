from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')
SBER_TOKEN  = os.getenv('SBER_TOKEN')