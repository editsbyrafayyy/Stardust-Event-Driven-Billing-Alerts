from pydantic_settings import BaseSettings, SettingsConfigDict
'''
The BaseSettings class specifically designed for system configuration management, similar to BaseModel (which validates data coming
from an API request) BaseSettings looks at os environment variables/files to fetch data 
'''

class Settings(BaseSettings): # this class serves as the template for the variables inside it to be mapped to env vars
	database_url : str # pydantic will automatically search system env/.env files for variables with this name
	secret_key: str
	redis_url: str = "redis://redis:6379/0" # flexible connection string for local dev, Docker Compose, or Cloud

	model_config = SettingsConfigDict(env_file=".env", extra="ignore") # extra='ignore' prevents errors on unexpected env vars


settings = Settings() # opens the .env file, gets the value from var, validates the string, loads into mem