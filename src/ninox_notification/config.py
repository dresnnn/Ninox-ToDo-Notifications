import yaml
from dataclasses import dataclass


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
    persons_table_id: str
    api_token: str


@dataclass
class Config:
    ninox: NinoxConfig
    smtp: SMTPConfig
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

    ninox_data = data["ninox"]
    ninox = NinoxConfig(**ninox_data)
    smtp = SMTPConfig(**data["smtp"])
    send_time = data.get("send_time", "09:00")
    debug = data.get("debug", False)

    return Config(ninox=ninox, smtp=smtp, send_time=send_time, debug=debug)
