import os

from dotenv import load_dotenv

load_dotenv()


def database_url() -> str:
    return os.environ["DATABASE_URL"]
