import os
import tweepy
from dotenv import dotenv_values
import traceback
import feedparser
from datetime import datetime
import json
import sys
from requests_oauthlib import OAuth1Session

# Load environment variables from .env file in the home directory
env_path = os.path.expanduser("~/.env")
env_vars = dotenv_values(env_path)

# Get the credentials from the loaded environment variables
consumer_key = env_vars['TWITTER_API_KEY']
consumer_secret = env_vars['TWITTER_API_SECRET']
access_token = env_vars['TWITTER_TOKEN_ACCESS']
access_token_secret = env_vars['TWITTER_TOKEN_SECRET']
bearer_token = env_vars['TWITTER_TOKEN_BEARER']
oauth_id = env_vars['TWITTER_OAUTH2_ID']
oauth_secret = env_vars['TWITTER_OAUTH2_SECRET']

print("consumer_key: {}".format(consumer_key))
print("consumer_secret: {}".format(consumer_secret))
print("token: {}".format(access_token))
print("token_secret: {}".format(access_token_secret))

# Define the file name
TOKEN_FILE = os.path.join( os.path.dirname(os.path.abspath( __file__ )),'.env.local');
#{"SOURCE":{"timeStamp":"<TIMESTAMP>","formatString":"<FORMAT>"}}
CACHE_FILE = os.path.join( os.path.dirname(os.path.abspath( __file__ )),".cache-twitter-uploader.json");

def load_credentials():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            return json.load(file)
    return None

def save_credentials(resource_owner_key, resource_owner_secret):
    with open(TOKEN_FILE, 'w') as file:
        json.dump({'oauth_token': resource_owner_key, 'oauth_token_secret': resource_owner_secret}, file)

def postToTwitter( msg , footer ):
    try:
        payload = {"text": "{}\n{}".format(msg,footer)}
        # Load credentials
        resource_owner_key = None;
        resource_owner_secret = None;
        credentials = load_credentials()
        if credentials:
            resource_owner_key = credentials['oauth_token']
            resource_owner_secret = credentials['oauth_token_secret']
            print(f"Loaded Key: {resource_owner_key}")
            print(f"Loaded Secret: {resource_owner_secret}")
        else:
            # Get request token
            request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
            oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
            try:
                fetch_response = oauth.fetch_request_token(request_token_url)
            except ValueError:
                print("There may have been an issue with the consumer_key or consumer_secret you entered.")
            resource_owner_key = fetch_response.get("oauth_token")
            resource_owner_secret = fetch_response.get("oauth_token_secret")
            save_credentials(resource_owner_key, resource_owner_secret)
            print("Got OAuth token: %s" % resource_owner_key)
            # Get authorization
            base_authorization_url = "https://api.twitter.com/oauth/authorize"
            authorization_url = oauth.authorization_url(base_authorization_url)
            print("Please go here and authorize: %s" % authorization_url)
            verifier = input("Paste the PIN here: ")
            # Get the access token
            access_token_url = "https://api.twitter.com/oauth/access_token"
            oauth = OAuth1Session( consumer_key, client_secret=consumer_secret,
                resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret, verifier=verifier, )
            oauth_tokens = oauth.fetch_access_token(access_token_url)
            resource_owner_key = oauth_tokens["oauth_token"]
            resource_owner_secret = oauth_tokens["oauth_token_secret"]
            save_credentials(resource_owner_key, resource_owner_secret)
        # Make the request
        oauth = OAuth1Session( consumer_key, client_secret=consumer_secret, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret,)
        # Making the request
        response = oauth.post( "https://api.twitter.com/2/tweets", json=payload,)

        if response.status_code != 201:
            if response.status_code == 401:
                pass 

            raise Exception( "Request returned an error: {} {}".format(response.status_code, response.text) )
            return False;
        print("Response code: {}".format(response.status_code))
        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        return True;
    except:
        traceback.print_exc()
        return False;


if __name__ == "__main__":
   
    # e.g.
    #pythonx ./twitterDoAPost.py "#poetry https://image.nostr.build/56ce4effdf7f5d50f45623b0e22907ae1f037a2c1274bdb054ee6654aca0626e.jpg" "#poem #englishculture"

    #program.py <msg> <tags>
    if len(sys.argv) > 1:
        footers = "";
        if len(sys.argv) > 2:
            footer = sys.argv[2];
        rslt = postToTwitter( sys.argv[1] , footer  );
    else:
        print("{} <RSS FEED>".format( sys.argv[0], ) );
