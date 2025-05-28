import yaml
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    from_address: str


@dataclass
class NinoxConfig:
    api_url: str
    team_id: str
    database_id: str
    table_id: str
    api_token: str


@dataclass
class User:
    email: str
    notify_in_debug: bool = False


@dataclass
class Config:
    ninox: NinoxConfig
    smtp: SMTPConfig
    users: Dict[str, User]
    send_time: str = "09:00"
    debug: bool = False


def load_config(path: str) -> Config:
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {path}: {e}")

    ninox = NinoxConfig(**data["ninox"])
    smtp = SMTPConfig(**data["smtp"])
    users = {name: User(**info) for name, info in data["users"].items()}
    send_time = data.get("send_time", "09:00")
    debug = data.get("debug", False)

    return Config(ninox=ninox, smtp=smtp, users=users, send_time=send_time, debug=debug)
