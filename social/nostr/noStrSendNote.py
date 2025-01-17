import os
import sys
from dotenv import dotenv_values
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
from pynostr.event import Event

# https://github.com/holgern/pynostr

conf = dotenv_values(os.path.expanduser("~/.env"))

npub = conf['NOSTR_PUB'];
nsec = conf['NOSTR_PRI'];

pubKey = PublicKey.from_npub( npub );
priKey = PrivateKey.from_nsec( nsec );

def getDM( msg, priKey ):
    dm = EncryptedDirectMessage()
    dm.encrypt(priKey.hex(),
      recipient_pubkey=pubKey.hex(),
      cleartext_content=msg
    )
    dm_event = dm.to_event()
    dm_event.sign(priKey.hex())
    return dm_event;

def run( msg ):
    relay_manager = RelayManager( timeout=6 );
    relay_manager.add_relay("wss://nostr-pub.wellorder.net")
    relay_manager.add_relay("wss://relay.damus.io")
    relay_manager.add_relay("wss://relay.nostr.bg")
    relay_manager.add_relay("wss://nos.lol")

    filters = FiltersList([Filters(authors=[pubKey.hex()], limit=1)])
    subscription_id = uuid.uuid1().hex
    relay_manager.add_subscription_on_all_relays(subscription_id, filters)
    
    event = Event( msg );
    event.sign( priKey.hex() );

    relay_manager.publish_event(event)
    relay_manager.run_sync()
    time.sleep(5) # allow the messages to send
    ok = None;
    while relay_manager.message_pool.has_ok_notices():
        ok_msg = relay_manager.message_pool.get_ok_notice()
        print(ok_msg)
        print("OK MSGS!")
        ok = ok_msg;
    while relay_manager.message_pool.has_events():
        event_msg = relay_manager.message_pool.get_event()
        print(event_msg.event.to_dict())
        ok = event_msg;
    return ok;

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run( sys.argv[1] );
    else:
        print("{} <TEXT_NOTE>".format( sys.argv[0], ) );
