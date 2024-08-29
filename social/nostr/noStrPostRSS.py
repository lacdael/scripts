import os
import sys
import time
import json
from dotenv import load_dotenv
import feedparser
from datetime import datetime
import noStrSendDM
import traceback

#{"SOURCE":{"timeStamp":"<TIMESTAMP>","formatString":"<FORMAT>"}}
CACHE_FILE = os.path.join( os.path.dirname(os.path.abspath( __file__ )),'.cache-noStr-uploader.json');
DEFAULT_FORMAT_STR = "%Y-%m-%dT%H:%M:%S%z";

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
        given_timestamp = datetime.strptime( "2024-04-08T12:43:45+00:00", DEFAULT_FORMAT_STR );
    data = get_posts_details(rss = feed_url) # return blogs data as a dictionary
    if data:
        post = getNextPost( data , given_timestamp );
        if post:
            print( post );
            print( "Send to noStr" )
            rslt = noStrSendDM.run( post["link"] );
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

    
