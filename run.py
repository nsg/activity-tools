import pprint

import src.actor

actor = src.actor.Actor("example.com", "user", "my-key")
pprint.pprint(actor.run())
