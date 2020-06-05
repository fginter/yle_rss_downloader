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
import requests
import gzip
import hashlib

import logging

THIS=os.path.abspath(os.path.dirname(__file__))
logging.basicConfig(filename=os.path.join(THIS,'rss.log'),format="%(asctime)s %(message)s", level=logging.INFO)
#logging.basicConfig(stream=sys.stderr,format="%(asctime)s %(message)s", level=logging.DEBUG)

def timestamp2datetime(s):
    return datetime.datetime.fromtimestamp(time.mktime(s))

def update_feed(*args,**kwargs):
    try:
        update_feed_unprotected(*args,**kwargs)
    except:
        logging.exception("something died")

def update_feed_unprotected(feed_url,feed_json_base,download_link):
    download_path=os.path.join(THIS,feed_json_base+"-downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)

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
        
    #grab the feed
    res=requests.get(feed_url)
    feed=feedparser.parse(res.text)

    appended=0
    #Now that we know which was the latest piece of news, if any
    for n in feed["items"]:
        dt = timestamp2datetime(n["published_parsed"])
        if latest is None or dt>latest:
            del n["published_parsed"]
            n["date_isoformat"]=dt.isoformat()
            news.append(n)
            if download_link:
                url=n.get("link",None)
                if url:
                    r=requests.get(url)
                    if r.status_code==200:
                        base=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+"---"+hashlib.md5(url.encode("utf-8")).hexdigest()+".html.gz"
                        with gzip.open(os.path.join(download_path,base),"wt") as f:
                            print(r.text,file=f)
                        time.sleep(1)
                    else:
                        logging.warning("Response code {} for {}".format(r.status_code,url))
                else:
                    logging.warning("No link!",n)
                    
            appended+=1
        else:
            pass
            #print("Skipping news from", dt, file=sys.stderr)
    if appended>0:
        logging.info("{} appended {} now have {}\n".format(feed_json_base, appended, len(news)))

    #And now we should have it all
    s=json.dumps(news,indent=4)
    with open(json_path,"w") as f:
        print(s,file=f)

        
try:
    logging.info("      ********** RUN ************\n\n")
    if not os.path.exists(os.path.join(THIS,"yle")):
        os.mkdir(os.path.join(THIS,"yle"))

    update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET","yle/yle-fi",True)
    update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_SELKOUUTISET","yle/yle-selko",True)
    update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NEWS","yle/yle-en",True)
    update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_SAPMI","yle/yle-saami",True)
    update_feed("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NOVOSTI","yle/yle-ru",True)
    update_feed("https://svenska.yle.fi/nyheter/senaste-nytt.rss","yle/yle-sv",True)
    update_feed("https://www.hs.fi/rss/tuoreimmat.xml","hs/hs-fi",True)
    update_feed("http://www.iltalehti.fi/rss/rss.xml","il/il",True)
    update_feed("https://www.mtv.fi/api/feed/rss/uutiset_uusimmat","mtv/mtv-uutis",True)
    update_feed("https://www.mtv.fi/api/feed/rss/urheilu","mtv/mtv-sport",True)
    update_feed("http://www.suomenuutiset.fi/?feed=rss2","persut/persut",True)
    update_feed("https://www.karjalainen.fi/component/obrss/karjalainen-uutiskirje","karjalainen/karjalainen",True)
    #update_feed("https://www.aamulehti.fi/?feed=uutiset&o=Tuoreimmat&k=0&ma=0&c=9,6,2,8,4,11,7,3,10,5","al/al",True) # dead link
    update_feed("https://ls24.fi/rss","lansisuomi/lansisuomi-uutis",True)
    update_feed("https://ls24.fi/urheilu/rss","lansisuomi/lansisuomi-sport",True)
    update_feed("https://ls24.fi/raumalainen/rss","raumalainen/raumalainen",True)
    update_feed("http://kiekkoareena.fi/rss","kiekkoareena/kiekkoareena",True)
    update_feed("https://www.kainuunsanomat.fi/feed/kaikki-uutiset?lehti=ylä-kainuu","ylakainuu/ylakainuu",True)
    update_feed("https://feeds.kauppalehti.fi/rss/main","kl/kl",True)
    update_feed("http://www.kaleva.fi/rss/show/","kaleva/kaleva",True)
    update_feed("https://www.lapinkansa.fi/feedit/rss/newest-free/","lapinkansa/lapinkansa",True)
    update_feed("https://www.is.fi/rss/tuoreimmat.xml","is/is",True)
    update_feed("https://www.kp24.fi/feed","kp24/kp24",True)
    #update_feed("https://www.satakunnankansa.fi/?feed=uutiset&o=Tuoreimmat%20uutiset&k=0&ma=0&c=11,8,2,7,12,5,10,4,3,6","skunnank/skunnank",True) # dead link
    update_feed("https://www.jatkoaika.com/rss/index.rss", "jatkoaika/jatkoaika", True)
    update_feed("https://www.hbl.fi/rss.xml", "hbl/hbl", True)

    # new feeds
    update_feed("https://www.talouselama.fi/api/feed/v2/rss/te", "talouselama/talouselama", True)
    update_feed("https://www.kansanuutiset.fi/feed", "kansanuutiset/kansanuutiset", True)
    update_feed("https://www.sss.fi/feed","salon/salon", True)
    update_feed("https://www.suomenmaa.fi/neo/neoproxy.dll?tem=rss_neo","suomenmaa/suomenmaa", True)
    update_feed("https://www.ts.fi/rss.xml","ts/ts", True)
    update_feed("https://www.verkkouutiset.fi/rss","verkkouutiset/verkkouutiset", True)
    update_feed("https://www.alandstidningen.ax/rss/allt","alands/alands", True)
    update_feed("https://www.nyan.ax/rss","nyan/nyan", True)
    update_feed("https://news.abounderrattelser.fi/rss","abou/abou", True)

    
except:
    logging.exception("uaaaa")

