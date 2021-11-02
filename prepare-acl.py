import argparse

import requests


def user_43(n):
    return {"username": f"u{n}", "password": "pass"}


def user_42(n):
    return {"login": f"u{n}", "password": "pass", "is_superuser": False}


def acl_43(n):
    return [
        {
            "username": f"u{n}",
            "topic": f"/a/{n}/#",
            "action": "pubsub",
            "access": "deny",
        },
        {
            "username": f"u{n}",
            "topic": f"/b/{n}/#",
            "action": "pubsub",
            "access": "allow",
        },
    ]


def acl_42(n):
    return [
        {
            "login": f"u{n}",
            "topic": f"/a/{n}/#",
            "action": "pubsub",
            "allow": False,
        },
        {
            "login": f"u{n}",
            "topic": f"/b/{n}/#",
            "action": "pubsub",
            "allow": True,
        },
    ]


VARIANTS = {
    "4.3": {
        "user_factory": user_43,
        "user_path": "auth_username",
        "acl_path": "acl",
        "acl_factory": acl_43,
    },
    "4.2": {
        "user_factory": user_42,
        "user_path": "mqtt_user",
        "acl_path": "mqtt_acl",
        "acl_factory": acl_42,
    },
}

CHUNK_SIZE = 1000


def chunks(lst):
    for i in range(0, len(lst), CHUNK_SIZE):
        yield lst[i : i + CHUNK_SIZE]


parser = argparse.ArgumentParser("prepare-acl")
parser.add_argument("version", type=str, choices=["4.3", "4.2"])
parser.add_argument("start_from", type=int, default=0)
parser.add_argument("count", type=int, default=5000)
parser.add_argument("--host", "-H", type=str, default="localhost")
parser.add_argument("--port", "-p", type=int, default=8081)

opts = parser.parse_args()

variant = VARIANTS[opts.version]
user_factory = variant["user_factory"]
acl_factory = variant["acl_factory"]

users = [user_factory(n) for n in range(opts.start_from, opts.start_from + opts.count)]
users_url = f"http://{opts.host}:{opts.port}/api/v4/{variant['user_path']}"

for user_chunk in chunks(users):
    print(f"Posting {len(user_chunk)} users to {users_url}")
    requests.post(
        users_url, json=user_chunk, auth=("admin", "public")
    ).raise_for_status()

acls = [
    acl
    for n in range(opts.start_from, opts.start_from + opts.count)
    for acl in acl_factory(n)
]
acls_url = f"http://{opts.host}:{opts.port}/api/v4/{variant['acl_path']}"

for acl_chunk in chunks(acls):
    print(f"Posting {len(acl_chunk)} acls to {acls_url}")
    requests.post(acls_url, json=acl_chunk, auth=("admin", "public")).raise_for_status()
