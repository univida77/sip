from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ENVIRONMENT:                str = "development"
    SQLITE_URL:                 str = "sqlite:///./parroquial.db"
    MYSQL_HOST:                 str = "localhost"
    MYSQL_PORT:                 int = 3306
    MYSQL_USER:                 str = "parroquial"
    MYSQL_PASSWORD:             str = "parroquial123"
    MYSQL_DB:                   str = "parroquial_db"
    SECRET_KEY:                 str = "clave_secreta_cambia_en_produccion"
    ALGORITHM:                  str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS:  int = 7
    ALLOWED_ORIGINS:            str = "http://localhost,http://localhost:8080,http://localhost:5000,http://127.0.0.1:8080,http://127.0.0.1:5000"
    ADMIN_EMAIL:                str = "admin@parroquia.mx"
    ADMIN_PASSWORD:             str = "admin123"
    ADMIN_NOMBRE:               str = "Administrador"
    ADMIN_APELLIDOS:            str = "Sistema"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def database_url(self) -> str:
        if self.is_production:
            return (
                f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            )
        return self.SQLITE_URL

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
