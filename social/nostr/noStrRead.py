from pynostr.relay import Relay
from pynostr.filters import FiltersList, Filters
from pynostr.event import EventKind
from pynostr.base_relay import RelayPolicy
from pynostr.message_pool import MessagePool
import tornado.ioloop
from tornado import gen
import time
import uuid
from pynostr.key import PublicKey
import os
import sys
from dotenv import load_dotenv

conf = dotenv_values(os.path.expanduser("~/.env"))

user_public_key = conf['NOSTR_PUB'];

def noStr_read():

    pubKey = PublicKey.from_npub( user_public_key );

    message_pool = MessagePool(first_response_only=False)
    policy = RelayPolicy()
    io_loop = tornado.ioloop.IOLoop.current()
    r = Relay(
        "wss://relay.damus.io",
        message_pool,
        io_loop,
        policy,
        timeout=2
    )
    filters = FiltersList([
        Filters(kinds=[EventKind.TEXT_NOTE], limit=100),
        Filters(authors=[pubKey.hex()])
        ])
    subscription_id = uuid.uuid1().hex

    r.add_subscription(subscription_id, filters)

    try:
        io_loop.run_sync(r.connect)
    except gen.Return:
        pass
    io_loop.stop()

    while message_pool.has_notices():
        notice_msg = message_pool.get_notice()
        print(notice_msg.content)
    while message_pool.has_events():
        event_msg = message_pool.get_event()
        print(event_msg.event.content)

def noStr_hex_pub():
    print( pubKey.hex() );

def noStr_send_DM():
    print("noStr DM");

def noStr_help( program ):
        print("{} [ -r ] [ -H ] [ -D <pub> <message> ]".format( sys.argv[0], ) );
            print("\t-r\t: read posts");
            print("\t-H\t: hex format of pub key");
            print("\t-D\t: Send <message> to <pub>");
 
if __name__ == "__main__":

    if len(sys.argv) < 2:
           sys.exit();

    if sys.argv[1] == "-r":
        noStr_read();
    elif sys.argv[1] == "-H":
        noStr_hex_pub();
    elif sys.argv[1] == "-D":
        noStr_send_DM();


