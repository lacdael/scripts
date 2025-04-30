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
from tarokGame import playParseText;

log = logging.getLogger(__name__)
# Load configuration

class NoStrDMHandler():

    def __init__(self, nsec, callback ):
        self.priKey = PrivateKey.from_nsec( nsec );
        #self.pubKey = self.priKey.public_key
        self.auth_event_ids = set();
        self.callback = callback;

    def add_relay_manager(self, relayMngr ):
        self.relayMngr = relayMngr;

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
        self.relayMngr.publish_event(dm_event)

    def publish_message_to_relay( self, relay_url , payload ):
        for relay in self.relayMngr.relays.values():
            if relay.url == relay_url:
                relay.ws.write_message( payload )
                break


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

            self.publish_message_to_relay(relay_url, json.dumps(auth_message))

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
                            self.callback( event , dm.cleartext_content );
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







dmMngr = None;


handled_event_ids = [];

def callback_handler( event , txt ):
    global dmMngr, handled_event_ids;
    if ( None != event and txt != "" ):
        try:
            if (event.id in handled_event_ids):
                return;
            handled_event_ids.append( event.id );
            if len( handled_event_ids ) > 500:
                handled_event_ids = handled_event_ids[1:]
            senderEventID = event.id
            senderPubKey = event.pubkey
            print("callback_handler")
            rsp = playParseText( txt, senderPubKey );
            print( rsp );
            if len( rsp ) != 3:
                return;
            #send_DM( PubKey , msg , event_id = None):
            dmMngr.send_DM( rsp[1] , rsp[0] )#, event.id );
            if None != rsp[2]:
                otherMsg = rsp[2][0];
                otherPubKey = rsp[2][1];
                if otherPubKey != None:
                    dmMngr.send_DM( otherPubKey, otherMsg );
        except:
            traceback.print_exc();


def run( nsec):
    global relay_manager, dmMngr;

    message_pool = MessagePool(first_response_only=True)
    policy = RelayPolicy()
    relay_manager = RelayManager(error_threshold=20,timeout=0 )
    
    relay_url_list = [
        "wss://nostr-pub.wellorder.net",
        "wss://relay.damus.io",
        "wss://relay.nostr.bg",
        "wss://nos.lol",
        "wss://auth.nostr1.com"
    ];
    
    relay_list = RelayList()
    relay_list.append_url_list( relay_url_list )

    dmMngr = NoStrDMHandler( nsec, callback_handler  );

    relay_manager.add_relay_list(
        relay_list,
        close_on_eose=False,
        message_callback=dmMngr.handle_message,
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
            since=get_timestamp(),
            #limit=100,
        )
        ]
    )

    subscription_id = uuid.uuid1().hex
    relay_manager.add_subscription_on_all_relays( subscription_id, filters )

   
    dmMngr.add_relay_manager( relay_manager )
    
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
        parser.add_argument('--priKeyEnvKey', required=True, type=str, help="env key for private Key.")
        parser.add_argument('--dataDir', required=False, type=str, help="path for data")
        args = parser.parse_args()
        
        conf = dotenv_values(os.path.expanduser("~/.env"))
        
        if args.priKeyEnvKey:
            nsec = conf[ args.priKeyEnvKey ]
            priKey = PrivateKey.from_nsec(nsec)
            pubKey = priKey.public_key;
            run( nsec );
    except:
        traceback.print_exc();

