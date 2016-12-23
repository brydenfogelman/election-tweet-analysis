import tweepy
import json
import time
import datetime
import os

QUERIES_DIR = 'day_after/'

# Retrieve Consumer/Auth Tokens from properties file
properties = dict(line.strip().split('=') for line in open('elections.properties') if not line.startswith('#') and not line.startswith('\n'))

# Setup authentication
auth = tweepy.OAuthHandler(properties["CONSUMER_KEY"], properties["CONSUMER_SECRET"])
auth.set_access_token(properties["OAUTH_TOKEN"], properties["OAUTH_TOKEN_SECRET"])
api = tweepy.API(auth)

def save_tweets(query, tweets_container, directory=None):
	'''
	Saves the dictionary of tweets to a file. The query and time stamp are used to save the files.

	@param:
		query - name for parent directory
		tweet_container - dictionary containing tweets
	'''
	if tweets_container:
		current_time = datetime.datetime.now()
		query_dir = QUERIES_DIR + query + '/'
		if directory:
			query_dir += directory + '/'

		if not os.path.exists(query_dir):
			os.makedirs(query_dir)

		with open(query_dir + current_time.isoformat() + '.json', 'w') as f:
			json.dump(tweets_container, f)

def limit_handled(cursor, query):
	'''
	Yields a tweet returned from a cursor. Yields none if an error occured while scraping tweets (namely for a rate limiting error).
	Reference: http://docs.tweepy.org/en/v3.5.0/code_snippet.html#handling-the-rate-limit-using-cursors

	@params:
		cursor - Tweepy cursor object
		query -  string used to find tweets
	'''

	while True:
		try:
			yield cursor.next()
		# catch stop iteration error
		except StopIteration as e:
			print "StopIteration for %s" % query
			print "\n"
			yield None
		# catch rate limit error
		except Exception as e:
			print "RATE LIMIT ERROR"
			print "%s: %s" % (query, e)
			print "\n"
			# can handle in any way we want
			print "\n"
			print "\n"
			print "\n"
			print "SLEEPING FOR 15 MINUTES"
			print "\n"
			time.sleep(15 * 60)
			yield None


def get_tweets(query, limit):
	'''
	Retrieves tweets from twitter api. Returns a dictionary keyed by tweet_id containing the tweet saved as json.
	'''
	tweets_container = {}

	'''
	TWEEPY CURSOR
	A cursor will continuosly iterate through tweets.
	Cursor params are passed to the method (ex.api.search)
	Cursor will alow as to continue to retrieve tweets without worrying about hitting a page limit

	api.search arguments are:

	    :reference: https://dev.twitter.com/rest/reference/get/search/tweets
	    :allowed_param:'q', 'lang', 'locale', 'since_id', 'geocode',
	     'max_id', 'since', 'until', 'result_type', 'count',
	      'include_entities', 'from', 'to', 'source']
	'''
	tweepy_cursor = tweepy.Cursor(api.search,
								q=query,
								count=100, # I think the correct param is rpp (but nvm it returns 100)
								result_type="recent", # We don't get enough results with this on
								include_entities=True,
								lang="en")
	size = 0
	for tweet in limit_handled(tweepy_cursor.items(), query):
		if not tweet:
			break
		# converting tweet to json
		tweet_json = json.dumps(tweet._json)
		tweet_json = json.loads(tweet_json)
		# To be able to retrieve the query later on
		tweet_json["from_query"] = query
		tweets_container[tweet_json['id']] = tweet_json

		# Test how many tweets we can store
		size = len(tweets_container.keys())
		if size % limit == 0:
			break

	print "Number of results: %d\n" % size
	return tweets_container

def get_and_save_tweets(queries, places, since=None, until=None, recent=None):
	'''

	'''

	nb_queries_per_search_term = len(places) + 1
	nb_queries_total = len(queries) * nb_queries_per_search_term

	print nb_queries_total

	nb_results_per_query = 100

	print nb_queries_total * nb_results_per_query

	limit = (180 / nb_queries_total) * nb_results_per_query

	for original_query in queries:
		query = original_query
		if since and until:
			query += " since:" + since + " until:" + until
			dr = since + "-" + until
		else:
			dr = recent
		print query
		tweets_container = get_tweets(query, limit=limit)
		save_tweets(original_query, tweets_container, directory=dr)

		for country, place_id in places.iteritems():
			print query, country
			query_place = "%s place:%s" % (query, place_id)
			tweets_container = get_tweets(query_place, limit=limit)
			if not tweets_container:
				print "No results for %s" % query_place
			else:
				save_tweets(original_query, tweets_container, directory=dr + "/" + country)

'''
MAIN LOOP
'''
if __name__ == "__main__":
	# Example Query
	# queries = [
	# 	"ElectionNight OR America",
	# 	"#DonaldTrump OR #HillaryClinton OR Trump OR Clinton OR #Trump OR #Clinton", 
	# 	"#Elections2016 OR #ElectionDay",  
	# 	"#ElectionFinalThoughts",
	# 	"stock OR market OR financial OR obama OR weed OR canadian OR mexico"
	# ]

	queries = [
		"protest AND trump",
		"peso AND trump",
		"wall AND trump",
		"canada AND trump",
		"election AND climate",
		"trump AND climate"
	]

	# Lookup dict for country locations
	places = {
		"USA": "96683cc9126741d1", 
		"Canada": "3376992a082d67c7", 
		"France": "f3bfc7dcc928977f", 
		"Denmark": "c29833e68a86e703",
		"Mexico": "25530ba03b7d90c6", 
		"Brazil": "1b107df3ccc0aaa1", 
		"Germany": "fdcd221ac44fa326", 
		"China": "4797714c95971ac1",
		"UK": "6416b8512febefc9", 
		"Russia": "5714382051c06d1e", 
		"Panama": "9d8ae4b0fac2036a", 
		"Australia": "3f14ce28dc7c4566",
		"Sweden": "82b141af443cb1b8", 
		"India": "b850c1bfd38f30e0", 
		"UAE": "3f63906fc8aa5a7d", 
		"South Africa": "dd9c0d7d7e07eb49",
	}

	try:
		while True:
			get_and_save_tweets(queries, places, recent="recent_nov9")
	except KeyboardInterrupt:
		pass
		