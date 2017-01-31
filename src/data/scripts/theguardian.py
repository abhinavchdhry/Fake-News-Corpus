import requests
import json
from lxml import html
import random

api_key = "63708ad5-70fd-42ad-8224-cc99a4a05409"
from_date = "2011-01-01"
to_date = "2016-01-31"
page_size = 200
base_url = "http://content.guardianapis.com/search"

headers = {
           "api-key" : api_key,
           "from-date" : from_date,
	   "to-date" : to_date,
	   "page-size" : str(page_size),
           "format" : "json",
           "page" : "1"
           }

filecounter = 0
misscount = 0

outfile = open("../rawdata/theguardian.com.data", "w")

r = requests.get(base_url, headers=headers)

if (r.status_code == 200):
    jsonData = json.loads(r.text)
    pages = jsonData['response']['pages']
    articleList = jsonData['response']['results']
    n = random.randint(0, len(articleList) - 1)
    article = articleList[n]
    json.dump(article, outfile)
    print("Total pages: ", pages)
    megalist = list()
    
    for p in range(2, pages+1):
        headers['page'] = str(p)
        print("Page: ", p)
        r = requests.get(base_url, headers)
        if (r.status_code == 200):
            jsonData = json.loads(r.text)
            articleList = jsonData['response']['results']
	    article = articleList[random.randint(0, len(articleList) - 1)]
	    outfile.write("\n")
	    json.dump(article, outfile)
#        print("...Done. Misscount = ", misscount)
#        if (p%20 == 0):
#            filename = "dumpfile" + str(filecounter)
#            filecounter = filecounter + 1
#            dump = open(filename, "w")
#            json.dump(megalist, dump)
