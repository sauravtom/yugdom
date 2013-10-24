#! /usr/bin/env python

#import tweepy
from bs4 import BeautifulSoup
import urllib2
import httplib2
import simplejson as json
from random import randint
import sys

'''
# == OAuth Authentication == using tweepy

consumer_key='YOUR_KEY'
consumer_secret='YOUR_KEY'
access_token='YOUR_KEY'
access_token_secret='YOUR_KEY'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
'''

Googl_key = 'YOUR_KEY'

def big_arr():
	arr1=tweet_hn_or_hsi('http://news.ycombinator.com/news')
	arr2=tweet_hn_or_hsi('http://hackerstreet.in/')
	arr3=tweet_from_xmlfeed('http://feeds.feedburner.com/SidebarFeed')
	arr4=tweet_from_xmlfeed('http://www.techmeme.com/feed.xml')
	tweet_from_xmlfeed('http://en.reddit.com/r/hacking/top/.rss')

def tweet_hn_or_hsi(url):
	arr=[]
	soup = BeautifulSoup( urllib2.urlopen(url).read() )

	for i in soup.find_all('td',{'class' : 'title'}):
		if len(i.get_text()) > 5:
			title= i.get_text()
			link= i.a.get('href')

			#FIND A BETER WAY TO DO THIS

			if len(title+link) <146 and 'Show HN' not in title and 'Show HSI' not in title and 'Ask HSI' not in title and 'Ask HN' not in title:
				tweet =title +" "+ shurl(link) +" #tech"
				arr.append(tweet)
	return arr
	#yugtweet( arr[ randint( 0,len(arr)-1 ) ] )


def tweet_from_svbtle():
	arr=[]
	url = 'https://svbtle.com/'
	soup = BeautifulSoup( urllib2.urlopen(url).read() )
	
	for i in soup.find_all('a'):
		if i.parent.name == 'article':
			twt=i.h1.get_text() +" "+shurl( i.get('href') ) +' via @svbtle'
			arr.append(twt)
	return arr
	#yugtweet( arr[ randint( 0,len(arr)-1 ) ] )


def tweet_from_xmlfeed(url):
	arr=[]

	headers = { 'User-Agent' : 'Yugdom 2.0 by /u/Tomarina github.com/sauravtom/yugdom' }
	req = urllib2.Request(url, None, headers)
	soup = BeautifulSoup( urllib2.urlopen(req).read() )

	for i in soup.find_all('item'):
		title = i.title.get_text()
		link = shurl( i.link.get_text() )

		try:
			i.description.get_text()
		except AttributeError:
			pass
			# what else could I write here ?
		else:
			desc = i.description.get_text()

		if 'the-pastry-box' in url:
			twt ='Pastry ' + title[title.find(',')+2:] + " " + link + " via @thepastrybox"
		elif 'techmeme' in url:
			twt =title + " " + link + " via @Techmeme"
		elif 'SidebarFeed' in url:
					twt =title + " " + link + " via @SidebarIO"
		elif 'hackerthings' in url:
					twt =title + " " + link + " via @Hackerthings"	
		elif 'reddit.com/r/' in url:
					start = desc.find('href=',25)
					end = desc.find('[link]')
					link = desc[start:end][6:-2]
					twt =title + ' ' + link				

		arr.append(twt)
	return arr
	#yugtweet( arr[ randint( 0,len(arr)-1 ) ] )
				

def follow_and_return_random_fellow():
	friends = []
	friends_of_friends = []
	
	master = api.get_user('yugdom')
	for f in master.friends():
		friends.append(f.screen_name)

	x=randint(0,len(friends)-1)	

	friend = api.get_user(friends[x])

	for f in friend.friends():
		friends_of_friends.append(f.screen_name)	

	x=randint(0,len(friends_of_friends)-1)
	random_f = friends_of_friends[x]
	
	print 'now following user ' + random_f
	api.create_friendship(random_f)	

	return random_f	
		

def yugtweet(tweet):
	tmp=[]
	for i in api.user_timeline('yugdom'):
		tmp.append(i.text)

	if tweet in tmp and len(tweet)<122:
		print 'Already tweeted that or too long a tweet maybe'
	else:
		tweet = check_escape_seq(tweet)
		if randint(1,100)%15 == 0:
			user = follow_and_return_random_fellow()
			twt = tweet + ' #NowFollowing @' + user
		else: twt = tweet

	if twt:
		print twt	
		api.update_status(twt)	

def check_escape_seq(s):
	s = s.replace("&lt;", "<")
	s = s.replace("&gt;", ">")
	s = s.replace("&amp;", "&")
	s = s.replace("&quot;", '"')
	s = s.replace("&apos;", "'")
	s = s.replace("&gt;", '>')
	s = s.replace("&lt;", '<')
	return s

def shurl(longUrl):
	if longUrl.startswith('http'):
		longUrl = longUrl
	else:
		longUrl = 'http://' + longUrl

	API_KEY = Googl_key
	apiUrl = 'https://www.googleapis.com/urlshortener/v1/url'
	headers = {"Content-type": "application/json"}
	data = {"longUrl": longUrl}
	h = httplib2.Http('.cache')

	try:
		headers, response = h.request(apiUrl, "POST", json.dumps(data), headers)
		short_url = json.loads(response)['id']

	except Exception, e:
		print "unexpected error %s" % e

	return short_url , longUrl

if __name__ == '__main__':
	r = randint(2,13);
	r=1;
	if r == 1: print 'foo'
	elif r == 2:	tweet_from_svbtle()
	elif r == 3:	tweet_hn_or_hsi('http://news.ycombinator.com/news')
	elif r == 4:	tweet_hn_or_hsi('http://hackerstreet.in/')
	elif r == 5:	tweet_from_xmlfeed('http://feeds.feedburner.com/SidebarFeed')
	elif r == 6:	tweet_from_xmlfeed('http://feeds.feedburner.com/hackerthings')
	elif r == 7:	tweet_from_xmlfeed('http://www.techmeme.com/feed.xml')
	elif r == 8:	tweet_from_xmlfeed('http://the-pastry-box-project.net/feed/')
	elif r == 9:	tweet_from_xmlfeed('http://en.reddit.com/r/technology/top/.rss')
	elif r == 10:	tweet_from_xmlfeed('http://en.reddit.com/r/geek/top/.rss')
	elif r == 11:	tweet_from_xmlfeed('http://en.reddit.com/r/hacking/top/.rss')
	elif r == 12:	tweet_from_xmlfeed('http://en.reddit.com/r/DIY/top/.rss')
	elif r == 13:	tweet_from_xmlfeed('http://en.reddit.com/r/LifeProTips/top/.rss')

''' 
Outline of yugdam 2.0

/bot/db once a day
will be where the magic happens and will be cronned periodically
import yugdam.py after modifying
each function in yugdam.py returns an array and each tweet in that array is stored in db

database updating happens once a day
displays recent entries in database.
entries in database are flushed daily
follow a random user once a day


/bot/tweet every 17th minute
get request contains a function which calls another function which extracts a weighted random 
tweet from db and tweets it every 17th minute
displays recently tweeted tweets

''' 