import pprint

from src.activity_tools.objects import Actor

actor = Actor("example.com", "user", "my-key")
pprint.pprint(actor.run())
