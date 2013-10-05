#!/usr/bin/env python

import cgi,urllib
from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import logging
from md5 import md5
import simplejson as json
import tweepy
import bitly
import urllib2

import simplejson as json
import logging
#import yugdom
from random import randint

from local_settings import TwitterKey, BitlyKey

class Matrix(db.Expando):
    data = db.TextProperty() #using text since string can only store 500 characters

class TwitterDB(db.Model):
    reddit_id = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)


class TwitterBot(webapp.RequestHandler):
    def get(self):
        consumer_key = TwitterKey['consumer_key']
        consumer_secret = TwitterKey['consumer_secret']
        access_token = TwitterKey['access_token']
        access_token_secret = TwitterKey['access_token_secret']

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        bot = tweepy.API(auth)

        q = db.GqlQuery("SELECT * FROM Matrix")

        for i in q:
            arr = json.loads(i.data)

        for i in arr:
            #print i
            pass

        r = randint( 0,len(arr)-1 )
        tweet = arr[r][0] + " " + arr[r][1]
        tmp=[]
        for i in bot.user_timeline('yugdom'):
            tmp.append(i.text)

        if tweet in tmp and len(tweet)<122:
            print 'Already tweeted that or too long a tweet maybe'
            logging.info('long tweet or already tweeted'+tweet)
        else:
            bot.update_status(tweet)
            logging.info('Successfully tweeted ' + tweet)
        #print url
        #print arr[r][1]

        self.response.out.write( "Just tweeted -> "+ arr[r][0] +" " + arr[r][1])

class Add_to_db(webapp.RequestHandler):
    def get(self):
        shortapi = bitly.Api(login=BitlyKey['login'], apikey=BitlyKey['apikey'])

        url = 'http://www.reddit.com/r/programming/.json'
        url = 'http://www.reddit.com/user/TakSlak/m/sfwporn/.json'
        
        arr = reddit_scrape(url)
        

        for i in arr:
            i[1] = shortapi.shorten( i[1] )

        for i in arr:
            print i[0]
            print i[1]

        #flush the database
        q = db.GqlQuery("SELECT * FROM Matrix")
        for i in q:
            i.delete()
        logging.info('Database successfully flushed')

        foo=Matrix()
        foo.data = json.dumps(arr)
        foo.put()
        logging.info('Database successfully updated')
        
        self.response.out.write("Database updated")
        

def reddit_scrape(url):
    arr=[]
    jsondata = json.loads(urllib2.urlopen(url).read())
        
    for i in jsondata["data"]["children"]:
        arr.append( [ i["data"]["title"] , i["data"]["url"] ])
    return arr



application = webapp.WSGIApplication([
    ('/tweet', TwitterBot),
    ('/db', Add_to_db)],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
	main()          
