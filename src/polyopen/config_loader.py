import mashumaro.codecs.yaml as yaml_codec
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from enum import Enum


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

    config_file = '/home/pmorch/.config/polyopen/config.yaml'
    config = yaml_codec.decode(Path(config_file).read_bytes(), Config)
    return config
