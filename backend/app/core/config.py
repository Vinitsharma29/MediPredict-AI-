from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str
    jwt_secret: str
    field_enc_key: str
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"


<<<<<<< HEAD
settings = Settings()
=======
settings = Settings()
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
