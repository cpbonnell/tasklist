from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(verbose=True)


class Configuration(BaseSettings):
    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_audience: str
    app_secret_key: str
