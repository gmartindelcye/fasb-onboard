from dotenv import dotenv_values, find_dotenv

env_file = find_dotenv('.env')

settings = dotenv_values(dotenv_path=env_file)

DB_USER = settings["DB_USER"]
DB_PASSWORD = settings["DB_PASSWORD"]
DB_HOST = settings["DB_HOST"]
DB_PORT = settings["DB_PORT"]
DB_DB = settings["DB_DB"]

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DB}"

APP_NAME = settings["APP_NAME"]
APP_VERSION = settings["APP_VERSION"]
APP_SUMMARY = settings["APP_SUMMARY"]
APP_DESCRIPTION = settings["APP_DESCRIPTION"]