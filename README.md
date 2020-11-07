# COVID-19-Sentiment-Analysis.

<h3>AI sentiment analysis and NLP(natural language process) project for over 6.000 "live" tweets about COVID-19.</h3>

* DataSet of Tweets was taken from Tweeter API by its "listener" objects from (17:00 -> 22:00) worldwide on 11/07/2020(D/M/Y).
* The project was implemented with Python through Twitter API and OpenMapQuest API. 
* Use of TextBlob's polarity property for sentiment analysis of a tweet.
* Every function has a small documentation inside for every object and utility.
* Csv file contains every tweet we processed through.
* Html file, contains a map with live locations and text from all the tweets we processed.
* On Html file, red marker defines a negative tweet, green marker a positive one ans gray marker on that's close to negative.
* In Stats file u can find some prtsrcns with statistics.

* Project implemeted with these small steps :
1) Make a twitter developer account, get access to its API.(A descent amount of tweets are available).
2) Make an openMapQuest developer account, get access to its API(A bit slow in free edition).
3) Install the libraries(First section of the project desribes them).
3) Create the APIs as python objects(inherit from specific classes, get advnantage of Inheritance).
4) Start to listen for tweets of a specific topic.
5) Clear the tweets from "useless" information through NLP.
5) Save them and draw them in Map.
6) Learn from the stats.

<h3>Some Results:</h3>

* 50% of tweets have a positive meaning and the other 50% have negative meaning.
* Most of tweets associate Covid-19 with Biden or Trump(cause today Biden won #USElections) 
* Russia hates Twitter.
* Africa made more tweets than Russia.

