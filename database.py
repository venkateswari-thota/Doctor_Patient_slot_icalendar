from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Local MongoDB usually does not require username/password
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "icalendar"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
client = AsyncIOMotorClient(settings.mongodb_url)
db = client[settings.database_name]
