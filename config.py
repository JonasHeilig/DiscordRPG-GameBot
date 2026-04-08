import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5505))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "bot", "game.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

ORE_TYPES = {
    "coal": 1,
    "iron": 2,
    "gold": 3,
    "copper": 4,
    "diamond": 5,
    "emerald": 6
}

DEFAULT_ORE_PROBABILITIES = {
    "coal": 40,
    "iron": 25,
    "gold": 15,
    "copper": 10,
    "diamond": 7,
    "emerald": 3
}

MAX_PLAYER_HEALTH = 100
