from typing import Optional, Union, Dict, Any
from flask import Flask
from redis import Redis


class FlaskRedis:
    _redis_client: Redis
    config_key: str
    _provider_kwargs: Dict[str, Any]
    _provider_class: Any

    def __init__(
        self,
        app: Flask = None,
        strict: bool = True,
        config_key: str = "REDIS_URI",
        **kwargs
    ):
        self._config_key = config_key
        self._provider_kwargs = kwargs
        self._provider_class = Redis
        if app:
            self.init_app(app)

    def init_app(self, app: Flask, **kwargs):
        redis_url = app.config.get(self._config_key, "redis://localhost:6379/0")
        self._provider_kwargs.update(kwargs)
        self._redis_client = self._provider_class.from_url(
            redis_url, **self._provider_kwargs
        )
        if not app.extensions:
            app.extensions = {}
        app.extensions["redis".lower()] = self

    @property
    def client(self) -> Redis:
        return self._redis_client
