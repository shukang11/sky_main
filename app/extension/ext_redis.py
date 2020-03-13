from typing import Optional, Union, Dict, Any
from flask import Flask
from redis import Redis, StrictRedis


class FlaskRedis:
    _redis_client: Union[Redis, StrictRedis, None]
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
        self._redis_client = None
        self._config_key = config_key
        self._provider_kwargs = kwargs
        self._provider_class = StrictRedis if strict else Redis
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

    def __getattr__(self, name):
        return getattr(self._redis_client, name)

    def __getitem__(self, name):
        return self._redis_client[name]

    def __setitem__(self, name, value):
        self._redis_client[name] = value

    def __delitem__(self, name):
        del self._redis_client[name]
