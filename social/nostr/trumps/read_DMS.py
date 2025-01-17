#!/usr/bin/env python
import getpass
import uuid
import json
import tornado.ioloop
from tornado import gen
import time
from pynostr.base_relay import RelayPolicy
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.event import Event, EventKind
from pynostr.filters import Filters, FiltersList
from pynostr.key import PrivateKey
from pynostr.message_pool import MessagePool
from pynostr.message_type import RelayMessageType
from pynostr.relay import Relay
from pynostr.relay_list import RelayList
from pynostr.utils import get_public_key, get_timestamp
from dotenv import dotenv_values
import os
import sys 
import logging
from pynostr.key import PublicKey, PrivateKey
import traceback
from pynostr.relay_manager import RelayManager
import argparse

log = logging.getLogger(__name__)
# Load configuration



#TODO:
# 1. Make a class
# 2.

class NoStrDMHandler():

    def __init__(self, nsec, relayMngr, callback ):
        self.priKey = PrivateKey.from_nsec( nsec );
        #self.pubKey = self.priKey.public_key
        self.relayMngr = relayMngr;
        self.auth_event_ids = set();
        self.callback = callback;

    def send_DM(self, recieverPubKey, msg, event_id = None):
        dm = EncryptedDirectMessage()
        dm.encrypt( 
            self.priKey.hex(),
            recipient_pubkey=recieverPubKey,
            cleartext_content=msg
        )
        dm_event = dm.to_event()
        if event_id:
            dm_event.add_event_ref( event_id ) 
        dm_event.sign( self.priKey.hex() )
        relay_manager.publish_event(dm_event)

    def handle_auth_message(self, challenge, relay_url):
        try:
            auth_event = Event(
                kind=22242,
                tags=[ ["relay", relay_url], ["challenge", challenge] ],
                content="",
                created_at=int(time.time())
            )
            auth_event.sign(priKey.hex())
            self.auth_event_ids.add(auth_event.id)
            auth_message = ["AUTH", auth_event.to_dict()]
            self.relayMngr.publish_message_to_relay(relay_url, json.dumps(auth_message))
        except Exception as e:
            print(f"Error in handle_auth_message: {e}")
            traceback.print_exc()

    def handle_message( self, message_json, relay_url ):#, r ):
        #global authSendID, eventIDs, challenge_to_IDs;
        try:
            message_type = message_json[0]
            if message_type == RelayMessageType.END_OF_STORED_EVENTS:
                print("EOSE: {}".format( message_json ) );
            elif message_type == RelayMessageType.EVENT:
                event = Event.from_dict(message_json[2])
                #if event.id in eventIDs:
                #    return;
                #eventIDs.append( event.id );
                if event.kind == EventKind.TEXT_NOTE:
                    print( "TEXT_NOTE");
                elif event.kind == EventKind.DIRECT_MESSAGE_KIND:
                    print("!DIRECT_MESSAGE_KIND");
                elif event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                    if event.has_pubkey_ref(priKey.public_key.hex()):
                        try: 
                            dm = EncryptedDirectMessage(reference_event_id=event.id)
                            dm.decrypt(self.priKey.hex(), event.content, event.pubkey )
                            print(dm.cleartext_content)
                            #self.handle_dm( dm.cleartext_content, event.id , event.pubkey )
                        except:
                            traceback.print_exc();
                            print( event );
                else:
                    print( message_type );
            elif message_type == RelayMessageType.OK:
                event_id = message_json[2]
                if event_id in self.auth_event_ids:
                    self.auth_event_ids.remove(event_id)
                    if message_json[3]:  # Success
                        self.relay_req(relay_url)
                    else:  # Retry authentication
                        self.handle_auth_message(None, relay_url)
            elif message_type == RelayMessageType.NOTICE:
                #print("NOTICE");
                print(message_json)
            elif message_type == RelayMessageType.AUTH:
                print("\t{}".format( message_json ));
                challenge = message_json[1];
                self.handle_auth_message( challenge, relay_url )
                #print(message_json)
            else:
                print( message_type );
        except:
            traceback.print_exc();

    def relay_REQ(self, relay_url ):
        try:
            filters = FiltersList([
                Filters(
                    kinds=[
                        #EventKind.TEXT_NOTE,
                        EventKind.ENCRYPTED_DIRECT_MESSAGE,
                        EventKind.DIRECT_MESSAGE_KIND
                    ],
                    pubkey_refs=[ self.priKey.public_key.hex() ]
                ),  # Only listen for direct messages (kind 4)
            ])
            subscription_id = uuid.uuid1().hex
            self.relayMngr.add_subscription_on_relay( relay_url, subscription_id, filters)
        except:
            traceback.print_exc();



































#npub = conf['NOSTR_PUB']
pubKey = None;
priKey = None;
#pubKey = PublicKey.from_npub(npub)
#priKey = PrivateKey.from_nsec(nsec)

relay_manager = None;
auth_event_ids = set()

def handle_auth_message(challenge, relay_url):
    try:
        
        # Create the authentication event
        auth_event = Event(
            kind=22242,
            tags=[
                ["relay", relay_url],
                ["challenge", challenge]
            ],
            content="",
            created_at=int(time.time())
        )
        auth_event.sign(priKey.hex())

        # Track the event ID
        auth_event_ids.add(auth_event.id)

        # Send the event
        auth_message = ["AUTH", auth_event.to_dict()]
        print("\t\t{}".format( auth_message ) ); 
        relay_manager.publish_message_to_relay(relay_url, json.dumps(auth_message))

    except Exception as e:
        print(f"Error in handle_auth_message: {e}")
        traceback.print_exc()



eventIDs = [];

def handle_dm( message , note_id=None , pubKey=None ):
    if relay_manager == None:
        return
    #TODO: store last timestamp
    #dm = EncryptedDirectMessage()
    #dm.encrypt(priKey.hex(),recipient_pubkey=pubKey,cleartext_content=message )
    #dm_event = dm.to_event()
    # ceate 'e' tag reference to the note you're replying to
    #if note_id != None:
    #    dm_event.add_event_ref( note_id) 
    #dm_event.sign(priKey.hex())
    #relay_manager.publish_event(dm_event)

def handle_message( message_json, relay_url ):#, r ):
    global authSendID, eventIDs, challenge_to_IDs;
    try:
        message_type = message_json[0]
        if message_type == RelayMessageType.END_OF_STORED_EVENTS:
            print("EOSE: {}".format( message_json ) );
        elif message_type == RelayMessageType.EVENT:
            event = Event.from_dict(message_json[2])
            if event.id in eventIDs:
                return;
            eventIDs.append( event.id );
            if event.kind == EventKind.TEXT_NOTE:
                
                print( "TEXT_NOTE");
                #for t in event.tags:
                #    if t[0] == "p":
                #        print("has p");
            elif event.kind == EventKind.DIRECT_MESSAGE_KIND:
                print("!DIRECT_MESSAGE_KIND");
            elif event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                if event.has_pubkey_ref(priKey.public_key.hex()):
                    try: 
                        your_private_key = priKey.hex()
                        your_public_key = priKey.public_key.hex()
                        dm = EncryptedDirectMessage(reference_event_id=event.id)
                        dm.decrypt(priKey.hex(), event.content, event.pubkey )
                        print(dm.cleartext_content)
                        handle_dm( dm.cleartext_content, event.id , event.pubkey )
                    except:
                        traceback.print_exc();
                        print( event );
            else:
                print( message_type );
        elif message_type == RelayMessageType.OK:
            event_id = message_json[2]
            if event_id in auth_event_ids:
                auth_event_ids.remove(event_id)
                if message_json[3]:  # Success
                    relay_req(relay_url)
                else:  # Retry authentication
                    handle_auth_message(None, relay_url)
        elif message_type == RelayMessageType.NOTICE:
            #print("NOTICE");
            print(message_json)
        elif message_type == RelayMessageType.AUTH:
            print("\t{}".format( message_json ));
            challenge = message_json[1];
            handle_auth_message( challenge, relay_url )
            #print(message_json)
        else:
            print( message_type );
    except:
        traceback.print_exc();




def relay_REQ( relay_url ):
    try:
        filters = FiltersList([
            Filters(
                kinds=[
                    #EventKind.TEXT_NOTE,
                    EventKind.ENCRYPTED_DIRECT_MESSAGE,
                    EventKind.DIRECT_MESSAGE_KIND
                ],
                pubkey_refs=[pubKey.hex()]
            ),  # Only listen for direct messages (kind 4)
        ])

        subscription_id = uuid.uuid1().hex
        relay_manager.add_subscription_on_relay( relay_url, subscription_id, filters)
    except:
        traceback.print_exc();


def run( nsec ):
    global relay_manager;

    message_pool = MessagePool(first_response_only=True)
    policy = RelayPolicy()
    relay_manager = RelayManager(error_threshold=20,timeout=0 if msg == None else 6 )
    
    relay_url_list = [
        "wss://nostr-pub.wellorder.net",
        "wss://relay.damus.io",
        "wss://relay.nostr.bg",
        "wss://nos.lol",
        "wss://auth.nostr1.com"
    ];
    
    relay_list = RelayList()
    relay_list.append_url_list( relay_url_list )

    relay_manager.add_relay_list(
        relay_list,
        close_on_eose=False,
        message_callback=handle_message,
        message_callback_url=True,
    )

    start_time = get_timestamp()

    filters = FiltersList( [
            Filters(
            kinds=[
                #EventKind.TEXT_NOTE,
                EventKind.ENCRYPTED_DIRECT_MESSAGE,
                EventKind.DIRECT_MESSAGE_KIND
            ],
            pubkey_refs=[pubKey.hex()],
            since=get_timestamp() if msg != None else 0,
            #limit=100,
        )
        ]
    )

    subscription_id = uuid.uuid1().hex
    relay_manager.add_subscription_on_all_relays( subscription_id, filters )

    if msg != None and pubKeyReciever != None:
        print( "Make and send DM");
        dm = EncryptedDirectMessage()
        dm.encrypt( 
            priKey.hex(),
            recipient_pubkey=pubKeyReciever,
            cleartext_content=msg
        )
        dm_event = dm.to_event()
        # ceate 'e' tag reference to the note you're replying to
        if event_id:
            dm_event.add_event_ref( event_id ) 
        dm_event.sign( priKey.hex() )
        relay_manager.publish_event(dm_event)
        
    def callback_handler():
        print("callback_handler")

    dmMnfr = NoStrDMHandler( nsec, relay_manager, callback_handler );
    
    try:
        relay_manager.run_sync()
        #io_loop.run_sync(relay_manager.run_sync)
        #relay_manager.open_connections()
    except:
        traceback.print_exc()
        pass

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Process command-line arguments for the program.")
        parser.add_argument('--msg', type=str, help="Message to send.")
        parser.add_argument('--eventID', type=str, help="Event ID needed for a reply.")
        parser.add_argument('--pubKeyReciever', type=str, help="public Key reciever.")
        parser.add_argument('--priKeyEnvKey', required=True, type=str, help="env key for private Key.")
        args = parser.parse_args()
        
        conf = dotenv_values(os.path.expanduser("~/.env"))
        
        if args.priKeyEnvKey:
            nsec = conf[ args.priKeyEnvKey ]
            priKey = PrivateKey.from_nsec(nsec)
            pubKey = priKey.public_key;
            run( nsec );
    except:
        traceback.print_exc();

