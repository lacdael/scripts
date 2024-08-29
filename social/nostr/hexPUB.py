import os
import sys
from dotenv import load_dotenv
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.key import PrivateKey
from pynostr.key import PublicKey
from pynostr.relay import Relay
from pynostr.relay_manager import RelayManager
from pynostr.filters import FiltersList, Filters
from pynostr.event import EventKind
from pynostr.base_relay import RelayPolicy
from pynostr.message_pool import MessagePool
import tornado.ioloop
from tornado import gen
import time
import uuid

# https://github.com/holgern/pynostr
conf = dotenv_values(os.path.expanduser("~/.env"))

npub = conf['NOSTR_PUB'];

pubKey = PublicKey.from_npub( npub );

print( pubKey.hex()  )
