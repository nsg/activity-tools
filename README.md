# activity-tools

This project contains building blocks that can be used to create ActivityPub applications.

## Actor

This generates basic actor that contains the needed bits to make Mastodon happy. 

```python
from activity_tools import actor

actor_domain = "example.com"
actor_user = "alice"
public_key = "..."

a = actor.Actor(actor_domain, actor_user, public_key)

print(a.run())
```

A few values like inbox URL defaults to `https://{actor_domain}/users/{actor_user}/inbox`. You can change this easily:

```
a.inbox = "https://localhost/actor/in"
a.outbox = "https://localhost/actor/out"

print(a.run())
```
