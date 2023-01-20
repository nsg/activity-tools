# activity-tools

This project contains building blocks that can be used to create ActivityPub applications.

## Actor

This generates basic actor that contains the needed bits to make Mastodon happy. 

```python
import activity-tools

actor_domain = "example.com"
actor_user = "alice"
public_key = ...

actor = activity-tools.actor.Actor(actor_domain, actor_user, public_key)

actor_dict = actor.run()
```

A few values like inbox URL defaults to `https://{actor_domain}/users/{actor_user}/inbox`. You can change this easily:

```
actor.inbox = f"https://{self.domain}/actor/{self.username}/in"
actor.outbox = f"https://{self.domain}/actor/{self.username}/out"
actor_dict = actor.run()
```
