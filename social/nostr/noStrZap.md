import pynostr
from pynostr.key import PrivateKey
from pynostr.event import Event

# Sender's private key
sender_private_key = PrivateKey()

# Sender's public key
sender_public_key = sender_private_key.public_key()

# The recipient's Nostr public key (example, in hex format)
recipient_public_key = "04c915daefee38317fa734444acee390a8269fe5810b2241e5e6dd343dfbecc9"

# The recipient's LNURL Pay URL (replace with actual URL)
recipient_lnurl = "lnurl1dp68gurn8ghj7um5v93kketj9ehx2amn9uh8wetvdskkkmn0wahz7mrww4excup0dajx2mrv92x9xp"

# Amount to send (in millisats)
amount = 21000

# Zap message (optional)
message = "Zap!"

# Create Zap Request event (kind 9734)
zap_request_event = Event(
    kind=9734,
    pubkey=sender_public_key,
    content=message,
    tags=[
        ["relays", "wss://nostr-pub.wellorder.com", "wss://anotherrelay.example.com"],
        ["amount", str(amount)],
        ["lnurl", recipient_lnurl],
        ["p", recipient_public_key],
    ]
)

# Sign the event with the sender's private key
zap_request_event.sign(sender_private_key)

# Print the event (for debugging)
print(zap_request_event)

# Send the zap request to recipient's LNURL Pay callback URL
zap_request_url = recipient_lnurl  # This is the LNURL Pay callback URL
# Here, you would use an HTTP client like `requests` to send the GET request with the zap request data
# Example: requests.get(zap_request_url, params=zap_request_event)

















import pynostr
from pynostr.event import Event

# Example: The recipient's LNURL Pay server sends a Zap Receipt after successful payment
def create_zap_receipt(zap_request_event, payment_confirmation):
    recipient_public_key = zap_request_event.tags[3][1]  # Extract recipient public key

    # Zap Receipt event (kind 9735)
    zap_receipt_event = Event(
        kind=9735,
        pubkey=recipient_public_key,
        content="Zap received and paid!",
        tags=[
            ["p", zap_request_event.tags[3][1]],  # sender's public key
            ["e", zap_request_event.id],  # Original zap request ID
        ]
    )

    # Sign the receipt event (this should be done by the recipient's wallet)
    zap_receipt_event.sign(PrivateKey())  # PrivateKey should be the recipient's private key

    # Send the receipt to the relays from the zap request (use the same relays as in the zap request)
    for relay_url in zap_request_event.tags[0][1:]:
        relay = pynostr.Relay(relay_url)
        relay.send(zap_receipt_event)

    return zap_receipt_event

# Example usage: assuming zap_request_event and payment_confirmation are available
zap_receipt = create_zap_receipt(zap_request_event, payment_confirmation)

# Print the zap receipt
print(zap_receipt)

