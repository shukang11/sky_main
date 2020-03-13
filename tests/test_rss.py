import pytest
import random
from .helper import *
from app.cold_data import RSS_SOURCES

rss_sources = RSS_SOURCES


def test_add_rss_source(client) -> int:
    token = get_token(client, DEFAULT_LOGIN_PARAMS)
    rss = random.choice(rss_sources)
    rv = client.post("/rss/add", json={"source": rss}, headers={"token": token})
    assert rv.status_code == 200
    body = rv.json["data"]
    assert body.get("rss_id") != 0
    return body.get("rss_id")


def test_remove_rss_source(client):
    rss_id = test_add_rss_source(client)
    token = get_token(client, DEFAULT_LOGIN_PARAMS)
    rv = client.post("/rss/remove", json={"rss_id": rss_id}, headers={"token": token})
    assert rv.status_code == 200
    body = rv.json["data"]
    print(body)


def test_rss_list_limit(client):
    token = get_token(client, DEFAULT_LOGIN_PARAMS)
    rv = client.get("/rss/limit", headers={"token": token})
    assert rv.status_code == 200
    body = rv.json["data"]
    assert body != None

def test_rss_content_list_limit(client):
    token = get_token(client, DEFAULT_LOGIN_PARAMS)
    rv = client.get("/rss/content/limit", headers={"token": token})
    assert rv.status_code == 200
    body = rv.json["data"]
    assert body != None
