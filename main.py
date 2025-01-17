
from datetime import datetime
import nltk
import time
import json
import tweepy
import preprocessor as p
p.set_options(p.OPT.URL, p.OPT.EMOJI)
import pprint
import os
import re
from twitter_sentiment_classifier import batch_predict

def load_credentials():
    cred = open('credentials/twitter_credentials.json')
    return cred

def parseItemHandler(parseItemList):
    if parseItemList != None:
        returnList = []
        for p in parseItemList:
            print(p)
            returnList.append(p.match)

        return returnList

    else:
        return None

def conductSA(text_list):
    return batch_predict(text_list)

def query_tweets(client,user,keyword,start_time,end_time):
    json_list = []

    query_string = ''

    if user != '':
        query_string += 'from:' + user
    if keyword != '':
        query_string += ' ' + keyword

    query_string += ' -is:retweet lang:nl place_country:BE'
    print(query_string)

    tweets = tweepy.Paginator(client.search_all_tweets,
                              query=query_string,
                              tweet_fields=[
                                  'created_at','id',"author_id","public_metrics"],
                              start_time=start_time+"-01-01T00:00:00Z",
                              end_time=end_time+"-12-31T23:59:59Z",
                              max_results=500)

    if tweets:
        for t in tweets:
            print(t)
            print(type(t))
            if t.data:
                for tweet in t.data :
                    parsed_tweet = p.parse(tweet.text)
                    # if parsed_tweet.urls :
                    #     print(type(parsed_tweet.urls[0]))
                    cleaned_tweet_text = ''.join(p.clean(tweet.text))
                    json_obj = {
                        'mentions': re.findall("@(\w+)", tweet.text) if len(re.findall("@(\w+)", tweet.text)) != 0 else None,
                        'hashtags': re.findall("#(\w+)", tweet.text) if len(re.findall("#(\w+)", tweet.text)) != 0 else None,
                        'urls': parseItemHandler(parsed_tweet.urls),
                        'emojis': parseItemHandler(parsed_tweet.emojis),
                        'text': cleaned_tweet_text,
                        'created_at': tweet.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'author_id': tweet.author_id,
                        'public_metrics': tweet.public_metrics,
                        'id':tweet.id,
                        'sentiment':conductSA([str(cleaned_tweet_text)])[0]
                    }
                    pprint.pprint(json_obj)
                    json_list.append(json_obj)
    time.sleep(1)
    return json_list

def process_tweet(client,user,keyword,start_time,end_time,folder_path):

    filename = keyword if user == "" else user + '_' + keyword
    filename = start_time + "_" + end_time + "_" + filename
    with open(folder_path+"/"+filename+'.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(query_tweets(client,user,keyword,start_time,end_time)))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    f = load_credentials()
    data = json.load(f)

    folder_path_list = ["flemish_politician","flemish_government_confidence","federal_confidence"]# replace with the path to your folder

    for folder_path in folder_path_list:
        file_contents = []

        #read all keywords in a folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding='utf-8') as f:
                    lines = f.read()
                file_contents = file_contents + lines.split(",")

        for keyword in file_contents:
            client = tweepy.Client(data['bearer_token'])
            process_tweet(client,"",keyword,"2008","2018",folder_path)
            time.sleep(1)




