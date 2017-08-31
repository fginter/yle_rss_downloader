import six
assert six.PY3, "Run me with Python3"

import feedparser
import json
import datetime
import os.path
import dateutil.parser
import time
import sys
import os

import logging

THIS=os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(filename=os.path.join(THIS,'rss.log'),format="%(asctime)s %(message)s", level=logging.INFO)

def timestamp2datetime(s):
    return datetime.datetime.fromtimestamp(time.mktime(s))

def update_feed(feed_url,feed_json_base):
    feed=feedparser.parse(feed_url)

    #Now need to figure out which is the latest news we've got in the feed
    now=datetime.datetime.now()
    json_path=os.path.join(THIS,feed_json_base+"."+now.strftime("%Y-%m-%d")+".json")
    if os.path.exists(json_path):
        with open(json_path,"r") as f:
            news=json.load(f)
    else:
        news=[]

    latest=None
    for n in news:
        d=dateutil.parser.parse(n["date_isoformat"])
        if latest is None or d>latest:
            latest=d

    logging.info("{} latest news I have is from {}".format(feed_json_base,latest))

    appended=0
    #Now we know which was the latest piece of news, if any
    for n in feed["items"]:
        dt = timestamp2datetime(n["published_parsed"])
        if latest is None or dt>latest:
            del n["published_parsed"]
            n["date_isoformat"]=dt.isoformat()
            news.append(n)
            appended+=1
        else:
            pass
            #print("Skipping news from", dt, file=sys.stderr)
    logging.info("{} appended {} now have {}\n".format(feed_json_base, appended, len(news)))

    #And now we should have it all
    s=json.dumps(news,indent=4)
    with open(json_path,"w") as f:
        print(s,file=f)

if not os.path.exists(os.path.join(THIS,"yle")):
    os.mkdir(os.path.join(THIS,"yle"))
    
update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET","yle/yle-fi")
update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_SELKOUUTISET","yle/yle-selko")
update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NEWS","yle/yle-en")
update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_SAPMI","yle/yle-saami")
update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NOVOSTI","yle/yle-ru")
update_feed("https://svenska.yle.fi/nyheter/senaste-nytt.rss","yle/yle-sv")
