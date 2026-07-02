from asyncio import tasks
import os
import shutil
import sqlite3
import dateparser
import requests
from dotenv import load_dotenv
from core.backup import create_backup
from core.config import DATABASE
from core.memory import LAST_TASK_RESULTS
from flask import jsonify

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")



# pending tasks handler








