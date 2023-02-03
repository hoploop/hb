from typing import List

from pydantic import BaseModel, Field


def list_default():
    return []


class DatabaseEncryptionConfig(BaseModel):
    salt: str
    namespace: str


class DatabaseConfig(BaseModel):
    uri: str
    optional: str
    generic: str
    name: str
    encryption: DatabaseEncryptionConfig


class WSConfig(BaseModel):
    interval: int
    timeout: int


class ServerConfig(BaseModel):
    url: str


class TagConfig(BaseModel):
    name: str
    description: str


class ApiConfig(BaseModel):
    title: str
    version: str
    ws: WSConfig
    description: str
    host: str
    port: int
    reload: bool = True
    key: str
    cert: str
    servers: List[ServerConfig] = Field(default_factory=list_default)
    tags: List[TagConfig] = Field(default_factory=list_default)
    allow_hosts: List[str] = Field(default_factory=list_default)
    allow_credentials: bool = True
    arbitrary_types_allowed: bool = True
    allow_methods: List[str] = Field(default_factory=list_default)
    allow_headers: List[str] = Field(default_factory=list_default)


class Config(BaseModel):
    database: DatabaseConfig
    api: ApiConfig
    logging: dict
    logs_folder: str
