#!/usr/bin/env python

import urllib
from google.appengine.ext import db
from google.appengine.api import urlfetch

import logging
import json
import tweepy
import urllib2

import sys
import webapp2

#import yugdom
from random import randint

from local_settings import TwitterKey,googl_APIKEY

import re,string 

consumer_key = TwitterKey['consumer_key']
consumer_secret = TwitterKey['consumer_secret']
access_token = TwitterKey['access_token']
access_token_secret = TwitterKey['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
bot = tweepy.API(auth)


class Matrix(db.Expando):
    data = db.TextProperty() #using text since string can only store 500 characters


class TwitterBot(webapp2.RequestHandler):
    def get(self):
        q = db.GqlQuery("SELECT * FROM Matrix")
        arr=[]
        for i in q:
            arr = json.loads(i.data)

        r = randint( 0,len(arr)-1 )
        tweet = arr[r][0] + " " + arr[r][1]
        tmp=[]
        for i in bot.user_timeline('yugdom'):
            tmp.append(i.text)

        if tweet in tmp and len(tweet)<139:
            print 'Already tweeted that or too long a tweet maybe'
            logging.info('long tweet or already tweeted'+tweet)
        else:
            bot.update_status(tweet)
            logging.info('Successfully tweeted ' + tweet)

        self.response.out.write("Just tweeted -> "+ arr[r][0] +" " + arr[r][1] +" " + str(r))

class Add_to_db(webapp2.RequestHandler):
    def get(self):
        arr1=arr2=arr3=arr4=arr5=arr6=[]

        try:    arr1 = feed_scrape()
        except: pass
        try:    arr2 = reddit_scrape('http://www.reddit.com/r/technology/.json','#Tech')
        except: pass
        try:    arr3 = reddit_scrape('http://www.reddit.com/r/upliftingnews/.json','#Uplifting')
        except: pass
        try:    arr4 = reddit_scrape('http://www.reddit.com/r/FoodForThought+truereddit/.json','#FoodForThought')
        except: pass
        try:    arr5 = reddit_scrape('http://www.reddit.com/r/worldnews/.json','#Global')
        except: pass
        try:    arr6 = reddit_scrape('http://www.reddit.com/r/videoporn+EarthPornVids/.json','#Video')
        except: pass
        try:    arr7 = reddit_scrape('http://www.reddit.com/r/documentaries/.json','#Documentary')
        except: pass 
        try:    arr8 = reddit_scrape('http://www.reddit.com/r/BiographyFilms/.json','#Biography')
        except: pass

        arr = super_array([arr1,arr2,arr3,arr4,arr5,arr6,arr7,arr8])

        #flush the database
        q = db.GqlQuery("SELECT * FROM Matrix")
        for i in q:
            i.delete()
        logging.info('Database successfully flushed')

        #add new entries to database
        foo=Matrix()
        foo.data = json.dumps(arr)
        foo.put()
        logging.info('Database successfully updated with %d values' %(len(arr)))
        
        self.response.out.write("Database updated")
        
class Tests(webapp2.RequestHandler):
    def get(self):
        arr = super_array([ [[1,2],[3,4]],[],[[5,6],[7,8]],[]] )
        self.response.out.write(arr)

class Follow(webapp2.RequestHandler):
    def get(self):
        friends = []
        friends_of_friends = []
        
        master = bot.get_user('yugdom')
        for f in master.friends():
            friends.append(f.screen_name)

        x=randint(0,len(friends)-1) 

        friend = bot.get_user(friends[x])

        for f in friend.friends():
            friends_of_friends.append(f.screen_name)    

        x=randint(0,len(friends_of_friends)-1)
        random_f = friends_of_friends[x]
        
        bot.create_friendship(random_f)

        logging.info('now following user ' + random_f)
        self.response.out.write('now following user ' + random_f)



def googl_shortner(url):
    apiUrl = 'https://www.googleapis.com/urlshortener/v1/url?key=%s' % googl_APIKEY

    result = urlfetch.fetch(url=apiUrl,
        payload=json.dumps({"longUrl": url}),
        method=urlfetch.POST,
        headers={'Content-Type': 'application/json'})
    content = json.loads(result.content)
    return content['id']

def super_array(arr):
    super_arr=[]
    for i in arr:
        for j in i:
            super_arr.append(j)
    return super_arr        

def reddit_scrape(url,tag=''):
    arr=[]    
    jsondata = json.loads(urlfetch.fetch(url).content)
    #jsondata = json.loads(urllib2.urlopen(url).read())

    #make an array of title vs image links
    for i in jsondata["data"]["children"]:
        t= i["data"]["title"]
        u = i["data"]["url"]
        re.sub(r'[^a-zA-Z0-9]',' ', t)
        t = t + ' ' + tag
        if len(t+u) > 139:
            u = googl_shortner(u)

        arr.append([t,u])
        logging.info(arr[-1])
    return arr

def feed_scrape(url='http://api.ihackernews.com/page',tag='#HN'):
    arr=[]
    jsondata = json.loads(urlfetch.fetch(url).content)
    #jsondata = json.loads(urllib2.urlopen(url).read())

    for i in jsondata["items"]:
        t=i['title']
        u=i['url']
        re.sub(r'[^a-zA-Z0-9]',' ', t)
        t=t+' '+tag
        if len(t+u) > 139:
            u = googl_shortner(u)
        arr.append([t,u])
        logging.info(arr[-1])
        
    
    return arr


application = webapp2.WSGIApplication([
    ('/tweet', TwitterBot),
    ('/tests',Tests),
    ('/follow',Follow),
    ('/db', Add_to_db)],debug=True)



'''
TODO

/follow and add it to cron [DONE]

Make facebook bot as well

Add logs to a database and view them in the homepage

/tests to run tests [DONE]

add login to /db /tweet and /follow

'''