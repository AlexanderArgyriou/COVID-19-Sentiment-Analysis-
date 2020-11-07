#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tweepy                     # Twitter API Handling module.
import Keys                       # Contains my personal API keys for Twitter Developer.
from textblob import TextBlob     # AI module for sentiment measurement in a blob(text).
# from textblob.sentiments import NaiveBayesAnalyzer, could also test sentiment like b = Blob(Text, NaiveBayesAnalyzer() ) with this analyzer.
import preprocessor as p          # module to "clear" tweets.
import pandas as pd               # pandas library for dataset representation.
import folium                     # Module to create a map with out tweets.
from geopy import OpenMapQuest    # identify the geographical coordinates.
import time                       # time module for delay purposes.
from nltk.corpus import stopwords # module to clear useless words.
import matplotlib.pyplot as plt   # make the graph of words a bit better with a tight layout.
from operator import itemgetter   # For sorting puposes module


# In[ ]:


def CreateTwitterAPI() :
    """ 
     A function that connects with my
    personal info from Keys.py to Twitter API and returns the 
    API object. 
    """
    
    # Authentication with MyTwitterDeveloper Infos.
    Auth = tweepy.OAuthHandler( Keys.APIkey, Keys.APIkeySecret )
    Auth.set_access_token( Keys.AccessToken, Keys.SecretAccessToken )

    # API object to interact with Twitter.
    # Second param defines a delay of 15min when we overuse the API so we can be ok with Twitter Policy.
    # Third Argument lets us to know when we have to wait cause overuse.
    TheAPI = tweepy.API(Auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
    
    # return twitter's API object.
    return TheAPI


# In[ ]:


def GetGeocodes( ListOfTweets ) :
    """ 
     A Function to customize the list of dictionaries which 
    represents tweets, and add in every dictionary the GeoLocation.latitude
    and the GeoLocation.longitude attributes for the location of the tweet.
    """
    print( "Getting Coords..." )
    
    # Connect mapquest with my personal developer API key.
    Geo = OpenMapQuest( api_key = Keys.MapAPIKey )
    
    # number of tweets without locations.
    BadLocations = 0
    
    # traverse the tweet list.
    for Tweet in ListOfTweets :
        ProcessedFlag = False
        Delay = .1
        GeoLocation = ""
        
        # try to see if a tweet is processed and handle a connection failure or timeout(if we trigger one).
        while not ProcessedFlag :
            try :
                GeoLocation = Geo.geocode( Tweet["Location"] )
                ProcessedFlag = True
            except :
                print("Time out, trying again")
                time.sleep(Delay)
                Delay += .1
            
            # Add {"Latitude" : GeoLocation.latitude} and {"Longitude" : GeoLocation.longitude}
            # to our Tweet Dictionary.
            if GeoLocation :
                Tweet["Latitude"] = GeoLocation.latitude
                Tweet["Longitude"] = GeoLocation.longitude
            else :
                BadLocations += 1
    
    print("GeoCoding Done")
    
    # return the number of bad locations.
    return  BadLocations;


# In[ ]:


def GetTweetContent(Tweet, Location = False) :
    """
     A Function that takes a Tweet rerurned from a listener and
    makes a dictionary for this tweet, with the usefull info we need
    and not all tweet's info.
    """
    
    # The dictionary which represents the tweet.
    Fields = {}
    
    # { "Screen_name" : "user's name who made the tweet" }.
    Fields["Screen_name"] = Tweet.user.screen_name
    
    # Check if a tweet has 280 words limit and take the full text.
    try :
        # { "Text" : "Text of the tweet" }.
        Fields["Text"] = Tweet.extended_tweet["full_text"]
    except :
        # { "Text" : "Text of the tweet" }.
        Fields["Text"] = Tweet.text
    
    # if a tweet describe the location parse it to the dictionary.
    if Location :
        # { "Location" : "Where was the tweet from" }.
        Fields["Location"] = Tweet.user.location
    
    # Return the dictionary with the tweet's info.
    return Fields


# In[ ]:


def DrawTweetsOnMap(TweetsList) :
    """
     This function creates and draws the tweets on the Map.
    """
    
    # Create a DataFrame from the TweetsList
    DF = pd.DataFrame(TweetsList)
    
    # Drop NANs
    DF = DF.dropna()
    
    # Save all the info we gained
    DF.to_csv("TweetsInfo.csv")
    
    # Map Creation, starts from US.
    Map = folium.Map(location = [39.8283, -98.5795], tiles = "Stamen Terrain", zoom_start = 5, detect_retina = True)
    
    # for every Tweet in DataFrame we bring it to the map.
    for T in DF.itertuples() :
        Txt = ": ".join( list((T.Screen_name, T.Text)) ) 
        Popup = folium.Popup(Txt, parse_html = True)
        
        # Neutral emotion color
        Marker = folium.Marker( (T.Latitude, T.Longitude), popup = Popup, icon = folium.Icon(color = "gray"))
        
        if T.Sentiment == "-" :
            # Negative emotion color
            Marker = folium.Marker( (T.Latitude, T.Longitude), popup = Popup, icon = folium.Icon(color = "red"))
        elif T.Sentiment == "+" :
            # Positive emotion color
            Marker = folium.Marker( (T.Latitude, T.Longitude), popup = Popup, icon = folium.Icon(color = "green"))
            
        Marker.add_to(Map)

    # Saves the Map as html
    Map.save("tweet_map.html")


# In[ ]:


class Analyzer(tweepy.StreamListener) :
    """
     This class inherits the tweepy.StreamListener interface,
    and is responsible to "listen and analyze tweets of a specific subject."
    """
    def __init__(self, newAPI, newTopic, newLimit = 10) :
        """
         Analyzer's Constructor which is uses the setter 
        properties of our _private objects to set them.
        """
        self.CountsDict = {"TotalTweets" : 0, "Locations" : 0}           # Count the num of tweets and the Locations.
        self.SentDict = {"Positive" : 0, "Negative" : 0, "Neutral" : 0}  # Ditionary to count AI predictions about the sentiment of a tweet
        self.TweetsList = []                                             # The list of Tweets.
        self.Topic = newTopic                                            # The topic of our listener for example tweets for football.
        self._TWEET_LIMIT = newLimit                                     # TweetLimit CONST
        super().__init__(newAPI)                                         # Call to tweepy.StreamListener constructor.
        
    @property 
    def CountsDict(self) :
        """Get _CountsDict."""
        return self._CountsDict
    
    @CountsDict.setter
    def CountsDict(self, newCountsDict) :
        """Set _CountsDict."""
        self._CountsDict = newCountsDict
    
    @property 
    def TweetsList(self) :
        """Get _TweetsList."""
        return self._TweetsList
    
    @TweetsList.setter
    def TweetsList(self, newTweetsList) :
        """Set _TweetsList."""
        self._TweetsList = newTweetsList
    
    @property 
    def Topic(self) :
        """Get _Topic."""
        return self._Topic
    
    @Topic.setter
    def Topic(self, newTopic) :
        """Set _Topic."""
        self._Topic = newTopic
    
    @property 
    def SentDict(self) :
        """Get _SentDict."""
        return self._SentDict
    
    @Topic.setter
    def SentDict(self, newSentDict) :
        """Set _SentDict."""
        self._SentDict = newSentDict
        
    def on_status(self, Status) :
        """
         Override the on_status method we inherited from the base class.
        This method handles every incoming tweet from our listener.
        Status represent a tweet object.
        """
        
        # Get a dictionary with the valuable tweet's info which we described in the definition of this function above.
        TweetData = GetTweetContent(Status, Location = True)
        
        # ignore's retweets and off topic tweets.
        if(TweetData["Text"].startswith("RT") or self.Topic.lower() not in TweetData["Text"].lower()) :
            return
        
        # +1 to overall tweets count.
        self._CountsDict["TotalTweets"] += 1
        
        # handles tweets without a location.
        if not Status.user.location :
            return
        
        p.set_options(p.OPT.URL, p.OPT.RESERVED)
        TweetData["Text"] = p.clean(TweetData["Text"]) # Cleans the Text from urls and twitter reserved keywords.
        # Bl = TextBlob(Text, analyzer = NaiveBayesAnalyzer()).
        
        # analyze through AI the sentiment of a tweet.
        Bl = TextBlob(TweetData["Text"])
        Sentiment = ""
        
        if Bl.sentiment.polarity > 0 :
            Sentiment = "+"
            self._SentDict["Positive"] += 1
        elif Bl.sentiment.polarity < 0 :
            Sentiment = "-"
            self._SentDict["Negative"] += 1
        else :
            Sentiment = ""
            self._SentDict["Neutral"] += 1
        
        TweetData["Text"] = f"({Sentiment}) {TweetData['Text']}"
        self._CountsDict["Locations"] += 1 # +1 to the tweets with location
        TweetData["Sentiment"] = Sentiment # adds the Sentiment to TweetData Dictionary
        self._TweetsList.append(TweetData) # append the dictionary to the list of dictionaries
        #print(f"{Status.user.screen_name} : {TweetData['Text']}\n") # print Name : Tweet
        print(self._CountsDict["TotalTweets"], end = ",")
        
        # Return false and stop if we are above the limit of tweets.
        return self._CountsDict["TotalTweets"] <= self._TWEET_LIMIT


# In[ ]:


def main() :
    """
    Driver program.
    """
    
    # The keyword we wanna search tweets and analyze the sentiment of them.
    SEARCH_KEY = "COVID-19" 
    
    # New API object.
    TheAPI = CreateTwitterAPI()
    
    # New Analyzer object.
    An = Analyzer(TheAPI, SEARCH_KEY, newLimit = 10_000)

    # Start a sync listening.
    TStream = tweepy.Stream(auth = TheAPI.auth, listener = An) 
    TStream.filter(track = [SEARCH_KEY], languages = ["en"], is_async = False)
    
    # Connect to OpenMapQuest API, Write the Latitude Longitude of a location from a tweet in its dictionary.
    GetGeocodes(An.TweetsList)
    
    # Now we draw the the map, we pin the tweets also and savew our tweets set to a csv file.
    DrawTweetsOnMap(An.TweetsList)
    
    print("App finished : Success")


# In[ ]:


if __name__ == "__main__" :
    main()


# In[ ]:


# Some simple stats, about positive and negative tweets.
DF_Nums = pd.read_csv("TweetsInfo.csv")

Total = Pos = Neg = 0

for Sent in DF_Nums["Sentiment"] :
    if Sent == "+" :
        Pos += 1
    else :
        Neg += 1
        
Total = Pos + Neg

print(f"Positive tweets : {Pos}\nNegative Tweets : {Neg}\nTotal Tweets : {Total}\nPos% : {Pos * 100 / Total:.3f}%\nNeg% : {Neg * 100 / Total:.3f}%")


# In[ ]:


# some simple stats about words on tweets.
Txt = ""

# Make all tweets a single text.
for Text in DF["Text"] :
    Txt += Text

# Create a TextBlob object to anylze it
Blb = TextBlob(Txt)

# Take from the Blob a Dictionary like {"word : count"}.
Items = Blb.word_counts.items()

# Avoid "trash words".
SW = stopwords.words("english")
Items = [item for item in Items if item[0] not in SW]

# Sort the words descending by number of appearances.
Top20Words = sorted(Items, key = itemgetter(1), reverse = True)

# Take top 20 of them
Top20Words = Top20Words[1:23]
del Top20Words[1] # trash word checked
del Top20Words[9] # trash word checked
# Create a DF of thos top20 words and print a graph for it.
DF_Words = pd.DataFrame(Top20Words, columns = ["word", "count"])
TheAxes = DF_Words.plot.bar(x = "word", y = "count", legend = False)
plt.gcf().tight_layout()

