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
TOKEN_FILE = os.path.join( os.path.dirname(os.path.abspath( __file__ )),'.credentials');
#{"SOURCE":{"timeStamp":"<TIMESTAMP>","formatString":"<FORMAT>"}}
CACHE_FILE = os.path.join( os.path.dirname(os.path.abspath( __file__ )),".cache-twitter-uploader.json");
DEFAULT_FORMAT_STR = "%Y-%m-%dT%H:%M:%S%z";

def load_credentials():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            return json.load(file)
    return None

def save_credentials(resource_owner_key, resource_owner_secret):
    with open(TOKEN_FILE, 'w') as file:
        json.dump({'oauth_token': resource_owner_key, 'oauth_token_secret': resource_owner_secret}, file)


def get_access_tokens():
    try:
        # Step 1: Obtain request token
        request_token_url = "https://api.twitter.com/oauth/request_token"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
        fetch_response = oauth.fetch_request_token(request_token_url)
        resource_owner_key = fetch_response.get('oauth_token')
        resource_owner_secret = fetch_response.get('oauth_token_secret')

        # Step 2: Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: {}".format(authorization_url))
        verifier = input("Paste the PIN here: ")

        # Step 3: Obtain access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)
        save_credentials(oauth_tokens['oauth_token'], oauth_tokens['oauth_token_secret'])

        return oauth_tokens['oauth_token'], oauth_tokens['oauth_token_secret']
    except Exception as e:
        print(f"Error obtaining access tokens: {e}")
        return None, None



def _postToTwitter(msg):
    try:
        header = msg["title"]
        video = msg["link"]
        footer = "#spokenword #poetry #reading #ukculture #britishculture #poetryreading #englishpoetry"
        payload = {"text": "{}\n{}\n{}".format(header, video, footer)}

        # Load credentials
        credentials = load_credentials()
        if credentials:
            resource_owner_key = credentials['oauth_token']
            resource_owner_secret = credentials['oauth_token_secret']
        else:
            resource_owner_key, resource_owner_secret = get_access_tokens()
            if not resource_owner_key:
                return False

        # Create OAuth1Session with access tokens
        oauth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
        )

        # Make the request
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        if response.status_code != 201:
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )

        print("Response code: {}".format(response.status_code))
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return False








def postToTwitter( msg ):
    try:
        # Be sure to add replace the text of the with the text you wish to Tweet. You can also add parameters to post polls, quote Tweets, Tweet with reply settings, and Tweet to Super Followers in addition to other features.
        header = msg["title"]
        video = msg["link"];
        footer="#spokenword #poetry #reading #ukculture #britishculture #poetryreading #englishpoetry"

        payload = {"text": "{}\n{}\n{}".format(header,video,footer)}

       
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
                print(
                    "There may have been an issue with the consumer_key or consumer_secret you entered."
                )
            resource_owner_key = fetch_response.get("oauth_token")
            resource_owner_secret = fetch_response.get("oauth_token_secret")
            save_credentials(resource_owner_key, resource_owner_secret)
            print("No credentials found.")

            print("Got OAuth token: %s" % resource_owner_key)

            # Get authorization
            base_authorization_url = "https://api.twitter.com/oauth/authorize"
            authorization_url = oauth.authorization_url(base_authorization_url)
            print("Please go here and authorize: %s" % authorization_url)
            verifier = input("Paste the PIN here: ")

            # Get the access token
            access_token_url = "https://api.twitter.com/oauth/access_token"
            oauth = OAuth1Session(
                consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
            )
            oauth_tokens = oauth.fetch_access_token(access_token_url)

            resource_owner_key = oauth_tokens["oauth_token"]
            resource_owner_secret = oauth_tokens["oauth_token_secret"]
            
            save_credentials(resource_owner_key, resource_owner_secret)


        # Make the request
        oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        )

        # Making the request
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        if response.status_code != 201:
            if response.status_code == 401:
                #Exception: Request returned an error: 401 {
                #  "title": "Unauthorized",
                #  "type": "about:blank",
                #  "status": 401,
                #  "detail": "Unauthorized"
                #}
                #TODO: delete .credentials file
                pass 


            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )
            return False;

        print("Response code: {}".format(response.status_code))

        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        return True;
    except:
        traceback.print_exc()
        return False;





























def getCachedLastupload( source ):
    if os.path.exists( CACHE_FILE ):
        print("File exists.")
        with open( CACHE_FILE ) as json_file:
            data = json.load(json_file)
            if source in data:
                if ( "timeStamp" in data[source] ):
                    fmt = data[source]["formatString"] if "formatString" in data[source] else DEFAULT_FORMAT_STR;
                    try:
                        t = datetime.strptime( data[source]["timeStamp"],fmt);
                        return t;
                    except:
                        traceback.print_exc()
                        return None;
    return None;

def cacheLastUpload( source , stamp ):
    data = {}
    if os.path.exists( CACHE_FILE ):
        with open( CACHE_FILE ) as json_file:
            data = json.load(json_file)
    if source not in data:
        data[ source] = {};
    if "timeStamp" not in data[source]:
        data[source] = {"timeStamp":stamp};
    else:
        if "formatString" not in data[source]:
            data[source]["formatString"] = DEFAULT_FORMAT_STR;
        data[source]["timeStamp"] = stamp;

    # Dump JSON data to file
    with open( CACHE_FILE , 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print("JSON data has been dumped to:", CACHE_FILE)

def get_posts_details(rss=None):

	"""
	Take link of rss feed as argument
	"""
	if rss is not None:

		# import the library only when url for feed is passed

		# parsing blog feed
		blog_feed = blog_feed = feedparser.parse(rss)

		# getting lists of blog entries via .entries
		posts = blog_feed.entries

		# dictionary for holding posts details
		posts_details = {"Blog title" : blog_feed.feed.title,
						"Blog link" : blog_feed.feed.link}

		post_list = []

		# iterating over individual posts
		for post in posts:
			temp = dict()

			# if any post doesn't have information then throw error.
			try:
				temp["title"] = post.title
				temp["link"] = post.link
				temp["author"] = post.author
				temp["time_published"] = post.published
				temp["tags"] = [tag.term for tag in post.tags]
				temp["authors"] = [author.name for author in post.authors]
				temp["summary"] = post.summary
			except:
				pass

			post_list.append(temp)

		# storing lists of posts in the dictionary
		posts_details["posts"] = post_list

		return posts_details # returning the details which is dictionary
	else:
		return None

def getNextPost( data, given_timestamp ):
    post = None;
    if data:
        # printing as a json string with indentation level = 2
        #given_timestamp = datetime.strptime(given_timestamp_str, "%Y-%m-%dT%H:%M:%S%z")
        # Find the next post after the given timestamp
        next_post = None
        for post in data["posts"]:
            post_timestamp = datetime.strptime(post["time_published"], "%Y-%m-%dT%H:%M:%S%z")
            #post_timestamp = post["time_published"]
            if post_timestamp > given_timestamp:
                next_post = post
            elif post_timestamp <= given_timestamp:
                break
        # Print the next post
        if next_post:
            return next_post;
        else:
            return None;
    else:
	    print("None")
    return post;

def isRecentlyTouched(file_path, threshold_min=120):
    try:
        last_modified_time = os.path.getmtime(file_path)
        current_time = time.time()
        time_difference_seconds = current_time - last_modified_time
        time_difference_hours = time_difference_seconds / (60)
        if time_difference_hours > threshold_min:
            return False
        else:
            return True
    except:
        return False;

def run( feed_url ):
    print("Using feed: {}".format( feed_url ))
    t = getCachedLastupload( feed_url )
    if t:
        given_timestamp = t;
    else:
        given_timestamp = datetime.strptime( "2024-06-08T12:43:45+00:00", DEFAULT_FORMAT_STR );
    data = get_posts_details(rss = feed_url) # return blogs data as a dictionary
    if data:
        post = getNextPost( data , given_timestamp );
        if post:
            print( post );
            print( "Send to twitter" )
            rslt = postToTwitter( post );
            if rslt:
                print(" cache ")
                cacheLastUpload( feed_url , str(post["time_published"]) )
            print(rslt);
        else:
            print("No action.")
    else:
	    print("None")
    return False;

if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("{} <RSS FEED>".format( sys.argv[0], ) );
        sys.exit();
    
    for i, arg in enumerate(sys.argv[1:], start=1):
        if isRecentlyTouched( CACHE_FILE, 1 ):
            print("Recently actioned - ENDING");
            sys.exit();
        run( arg );

    

