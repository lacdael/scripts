import logging
import uuid

from rich.console import Console
from tornado import gen
import os
from pynostr.event import EventKind
from pynostr.filters import Filters, FiltersList
from pynostr.message_type import RelayMessageType
from pynostr.relay_list import RelayList
from pynostr.relay_manager import RelayManager
from pynostr.utils import get_public_key, get_relay_list, get_timestamp
from dotenv import dotenv_values
from pynostr.key import PublicKey, PrivateKey

log = logging.getLogger(__name__)

conf = dotenv_values(os.path.expanduser("~/.env"))
nsec = conf['NOSTR_PRI_TAROK'];
priKey = PrivateKey.from_nsec(nsec)
user_public_key = priKey.public_key.hex();


@gen.coroutine
def print_message(message_json, url):
    message_type = message_json[0]
    if message_type == RelayMessageType.EVENT:
        print(f"{url}: {str(message_json)}")


if __name__ == "__main__":

    console = Console()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch = logging.StreamHandler()
    ch.setLevel(4)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    identity = user_public_key;
    

    relay_list = RelayList()
    relay_list.append_url_list( [
        "wss://nostr-pub.wellorder.net",
        "wss://relay.damus.io",
        "wss://relay.nostr.bg",
        "wss://nos.lol",
        "wss://auth.nostr1.com" ] )

    print(f"Checking {len(relay_list.data)} relays...")

    relay_list.update_relay_information(timeout=0.5)
    relay_list.drop_empty_metadata()

    print(f"Found {len(relay_list.data)} relays...")

    # timeout must set to 0 and close_on_eose must set to False
    # When message_callback_url is set to True, message_callback function
    # must process also the url
    relay_manager = RelayManager(error_threshold=3, timeout=0)
    relay_manager.add_relay_list(
        relay_list,
        close_on_eose=False,
        message_callback=print_message,
        message_callback_url=True,
    )

    start_time = get_timestamp()

    filters = FiltersList(
        [  # enter filter condition
            Filters(
                since=start_time,
                kinds=[EventKind.TEXT_NOTE],
                pubkey_refs=[
                    user_public_key,
                ],
            )
        ]
    )
    subscription_id = uuid.uuid1().hex
    relay_manager.add_subscription_on_all_relays(subscription_id, filters)
    relay_manager.run_sync()
