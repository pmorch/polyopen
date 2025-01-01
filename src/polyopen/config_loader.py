from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import mashumaro.codecs.yaml as yaml_codec
from xdg_base_dirs import xdg_config_home


class Transport(Enum):
    websockets = "websockets"
    tcp = "tcp"


@dataclass
class Auth:
    username: str
    password: str


@dataclass
class Cert:
    required: bool


@dataclass
class MQTT:
    host: str
    port: int
    cert: Optional[Cert]
    transport: Transport
    auth: Optional[Auth]
    topicPrefix: Optional[str]
    keepalive: int = field(default=60)


@dataclass
class Config:
    MQTT: MQTT
    clientId: str
    publisherHostnames: list[str]
    subscriptions: list[str]
    destinations: list[str]


def load() -> Config:
    config_file = xdg_config_home() / "polyopen/config.yaml"
    if not config_file.exists():
        raise FileNotFoundError(f"{config_file} not found. See polyopen's README.md")
    config = yaml_codec.decode(Path(config_file).read_bytes(), Config)
    return config
