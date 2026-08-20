import os
from dataclasses import dataclass

def _bool(name, default=False):
    raw=os.getenv(name)
    return default if raw is None else raw.strip().lower() in {"1","true","yes","on"}

@dataclass(frozen=True)
class Settings:
    app_name:str=os.getenv("M99_APP_NAME","M99 Knowledge Platform")
    env:str=os.getenv("M99_ENV","development")
    host:str=os.getenv("M99_HOST","127.0.0.1")
    port:int=int(os.getenv("M99_PORT","8070"))
    database_url:str=os.getenv("M99_DATABASE_URL","sqlite:///./data/m99_admin.db")
    session_secret:str=os.getenv("M99_SESSION_SECRET","")
    session_https_only:bool=_bool("M99_SESSION_HTTPS_ONLY",False)
    session_max_age:int=int(os.getenv("M99_SESSION_MAX_AGE","28800"))
settings=Settings()
