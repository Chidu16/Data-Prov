import sys
import os
import csv
import json
import pymongo as mdb
import pprint
from collections import Counter
import view
import json
import datetime
from prov.nodes import *
from prov.edges import *
from prov.bind import *
import matplotlib.pyplot as plt
import tweepy
from aylienapiclient import textapi

import argparse
import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox

# FOAF = P_nspace("foaf", "http://xmlns.com/foaf/0.1/")
# ex = P_nspace("ex", "http://www.example.com/")
# dcterms = P_nspace("dcterms", "http://purl.org/dc/terms/")
# xsd = P_nspace("xsd", 'http://www.w3.org/2001/XMLSchema-datatypes#')
sentigraph = P_cont()
sentigraph.set_default_namespace("http://www.example.com/")
# sentigraph.add_namespace("foaf", "http://xmlns.com/foaf/0.1/")

attrdict = {"name": "Chidu"}
init = Agent("initiator", attributes=attrdict)
sentigraph.add(init)

starttime = datetime.datetime.utcnow().isoformat()
senti_alyz = Activity("sentiment_analysis")
sentigraph.add(senti_alyz)

# Twitter API creds
tweet_key = "tweet_key"
tweet_secret = "tweet_secret"
tweet_token = "tweet_token"
tweet_token_secret = "tweet_token_secret"

# AYLIEN credentials
ayl_id = "ayl_id"
ayl_key = "ayl_key"

# setting up twitter client
tweet_auth = tweepy.OAuthHandler(tweet_key, tweet_secret)
tweet_auth.set_access_token(tweet_token, tweet_token_secret)
api = tweepy.API(tweet_auth)

# creaating AYLIEN API client
client = textapi.Client(ayl_id, ayl_key)

# Twitter search query
query = input("What subject do you want to analyze for this example? \n")
limit = input("How many Tweets do you want to analyze? \n")

results = api.search(
    lang="en",
    q=query + " -rt",
    count=limit,
    result_type="recent"
)

attrdict = {"type": "query",
            "limit": limit,
            "string": query}
tweet_query = Activity("tweet_query", attributes=attrdict)
sentigraph.add(tweet_query)

print("--- Gathered Tweets \n")

# opening file to store output
f_name = 'TSA_About{}.csv'.format(query)

attrdict = {"type": "file",
            "path": f_name}

op_flie = Entity("op_flie", attributes=attrdict)
sentigraph.add(op_flie)

with open(f_name, 'w', newline='') as csvfile:
    csv_writer = csv.DictWriter(
        f=csvfile,
        fieldnames=["Tweet", "Sentiment"]
    )
    csv_writer.writeheader()

    print("--- Storing the output into csv file \n")

    # cleaning Tweets and sendingin to AYLIEN API
    for a, out in enumerate(results, start=1):
        tweet = out.text
        cleaned_tweet = tweet.strip().encode('ascii', 'ignore')

        if len(tweet) == 0:
            print('Empty Tweet')
            continue

        response = client.Sentiment({'text': cleaned_tweet})
        csv_writer.writerow({
            'Tweet': response['text'],
            'Sentiment': response['polarity']
        })

        t_name = 'tweet_{}'.format(a)
        print(t_name)
        attrdict = {"type": "tweet",
                    "tweet": response['text'],
                    "sentiment": response['polarity']}

        tweet_name = Entity(t_name, attributes=attrdict)
        sentigraph.add(tweet_name)

        u_name = 'uses_{}'.format(a)
        uses = Used(senti_alyz, tweet_name, identifier=u_name, time=None, attributes=None)
        sentigraph.add(uses)

        g_name = 'generated_tweet_{}'.format(a)
        gen_tweet = wasGeneratedBy(tweet_name, tweet_query, identifier=g_name, attributes=None)
        sentigraph.add(gen_tweet)

        print("Tweets Analyzed {}".format(a))

gen = wasGeneratedBy(op_flie, senti_alyz, identifier="generated", attributes=None)
sentigraph.add(gen)

started = wasAssociatedWith(senti_alyz, init, identifier="started", attributes=None)
sentigraph.add(started)

endtime = datetime.datetime.utcnow().isoformat()
senti_alyz = Activity("sentiment_analysis", starttime=starttime, endtime=endtime)
sentigraph.add(senti_alyz)

# printing json to file
j_name = 'provenance_{}'.format(query)
l = sentigraph.to_JSON
id = {"_id": j_name}
l.update(id)

j = json.dumps(l, indent=4)

f = open(j_name + '.json', "w")
f.write(j)
f.close()

m_client = mdb.MongoClient('localhost', 27017)
db = m_client['prov_db']
collection_prov = db['provenance']

with open(j_name + '.json', "r") as f:
    file_data = json.load(f)

id = collection_prov.insert_one(file_data)
# print("MongoDB Record id is ",id)
m_client.close()

# reading output from file and showing it on console
with open(f_name, 'r') as data:
    counter = Counter()
    for row in csv.DictReader(data):
        counter[row['Sentiment']] += 1

    positive = counter['positive']
    negative = counter['negative']
    neutral = counter['neutral']

colors = ['green', 'red', 'grey']
sizes = [positive, negative, neutral]
labels = 'Positive', 'Negative', 'Neutral'

plt.pie(
    x=sizes,
    shadow=True,
    colors=colors,
    labels=labels,
    startangle=90
)

plt.title("Sentiment of {} Tweets about {}".format(limit, query))
plt.show()

root = tk.Tk()
root.title('Prov JSON')
root.geometry("500x500")
menubar = tk.Menu(root)

path = j_name + '.json'
app = view.JSONTreeFrame(root, path)

app.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
root.columnconfigure(0, weight=3)
root.rowconfigure(0, weight=3)
root.mainloop()
