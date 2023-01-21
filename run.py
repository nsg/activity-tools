"""

This is an example application that uses activity-tools with FastAPI to create a
simple demo API that you can browse and follow from an Mastodon server.

If you have installed activity-tools via pip, change the imports from
"src.activity_tools" to activity_tools".

Start the application with:
$ uvicorn run:app --host 0.0.0.0 --workers 2

"""

import os
import json
import requests

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse

from src.activity_tools.objects import Actor, WrapActivityStreamsObject, Follow, Undo, Accept
from src.activity_tools.misc import PublicKey, WebFinger
from src.activity_tools.headers import ContentTypes, verify_signature, make_signature
from src.activity_tools.inbox import Inbox
from src.activity_tools.crypto import RSAKey

DOMAIN = os.getenv("DOMAIN", "example.com")
KEY = RSAKey("/tmp/key.pem")

app = FastAPI(
    title="ActivityPub Example Application",
    description="Let's see what I can do with a few lines of Python!",
    version="0.1.0"
)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    response = RedirectResponse(url='/docs')
    return response

@app.get("/.well-known/webfinger")
def webfinger(resource: str):
    content = WebFinger(DOMAIN, resource).run()
    return JSONResponse(content=content, headers=ContentTypes.jrd)

@app.get("/users/{username}")
def users(username: str):

    actor = Actor()
    actor.create(DOMAIN, username, KEY.public_key)
    actor.followers = None
    actor.following = None
    actor.outbox = None

    return JSONResponse(content=actor.run(), headers=ContentTypes.activity)

@app.get("/users/{username}/key")
def users(username: str):
    public_key = KEY.public_key
    content = WrapActivityStreamsObject(PublicKey(DOMAIN, username, public_key)).run()
    return JSONResponse(content=content, headers=ContentTypes.activity)

@app.post('/users/{username}/inbox')
async def inbox(username: str, request: Request):

    body = json.loads(await request.body())

    if not verify_signature(body, request.headers.items(), request.url.path):
        content = { "message": "Invalid signature" }
        return JSONResponse(
            content=content,
            headers=ContentTypes.activity,
            status_code=401
        )

    inbox = Inbox(body)
    object = inbox.parse()

    if type(object) == Follow:
        accept = Accept(DOMAIN, username, object.run())
        signature = make_signature(object)

        r = requests.post(
            object.actor.inbox,
            data=json.dumps(accept.run()),
            headers={ **ContentTypes.activity, **signature }
        )

        print(r.status_code, r.content)

    elif type(object) == Undo:
        print("We got a undo request!")
