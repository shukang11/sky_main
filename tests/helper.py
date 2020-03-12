


def get_token(client, email, password) -> str:
    rv = client.post("/user/login", json={"email": email, "password": password,})
    return rv.json["data"]["token"]

