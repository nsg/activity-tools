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

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse

from src.activity_tools.objects import Actor, WrapActivityStreamsObject, Follow, Undo
from src.activity_tools.misc import PublicKey, WebFinger
from src.activity_tools.headers import ContentTypes
from src.activity_tools.inbox import Inbox

DOMAIN = os.getenv("DOMAIN", "example.com")

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
    public_key = "123"

    actor = Actor()
    actor.create(DOMAIN, username, public_key)    
    actor.followers = None
    actor.following = None
    actor.outbox = None

    return JSONResponse(content=actor.run(), headers=ContentTypes.activity)

@app.get("/users/{username}/key")
def users(username: str):
    public_key = "123"
    content = WrapActivityStreamsObject(PublicKey(DOMAIN, username, public_key)).run()
    return JSONResponse(content=content, headers=ContentTypes.activity)

@app.post('/users/{username}/inbox')
async def inbox(username: str, request: Request):

    data = json.loads(await request.body())
    inbox = Inbox(data, request.headers, request.url.path)

    if not inbox.validate():
        content = { "message": "Invalid signature" }
        return JSONResponse(
            content=content,
            headers=ContentTypes.activity,
            status_code=401
        )

    object = inbox.parse()

    if type(object) == Follow:
        print("We got a follow request!")

    elif type(object) == Undo:
        print("We got a undo request!")
