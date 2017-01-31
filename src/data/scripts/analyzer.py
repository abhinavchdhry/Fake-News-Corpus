#from pyspark import SparkConf, SparkContext
import urllib2
from bs4 import BeautifulSoup as bs
import re
#import matplotlib.pyplot as plt
import hashlib
import json

#f = open("combined.txt", "r")
#conf = SparkConf().setMaster("local[2]").setAppName("Streamer")
#sc = SparkContext(conf=conf)

#data = sc.textFile("/home/achoudh3/Fake-News-Extraction-Scripts/OnionCrawler/data/combined.txt")

#r1 = re.compile("^http://www.enduringvision.com/news/([a-zA-Z]*)_([0-9]*)\.php$")
#r2 = re.compile("^http://www.newsbiscuit.com/([0-9]{4})/([0-9]{2})/([0-9]{2})/*")
#dr = re.compile("([0-9]{4})\-([0-9]{2})\-([0-9]{2})*")

def DateParser(d):
	if dr.match(d) is not None:
		return([int(dr.match(d).group(1)), int(dr.match(d).group(2)), int(dr.match(d).group(3))])
	else:
		return(None)

count = 0
def processor(line):
	try:
		if r1.match(line.strip()) is not None:
			date = r1.match(line.strip()).group(2)
			mm = int(date[0:2])
			dd = int(date[2:4])
			yy = int(date[4:6])
			if yy > 17:
				yy = 1900 + yy
			else:
				yy = 2000 + yy
			return([yy, mm, dd])
		elif r2.match(line.strip()) is not None:
			yyyy = int(r2.match(line.strip()).group(1))
			mm = int(r2.match(line.strip()).group(2))
			dd = int(r2.match(line.strip()).group(3))
			return([yyyy, mm, dd])
		else:
			parsed = bs(urllib2.urlopen(line.strip()).read(), "html.parser")
			d = parsed.find('meta', property="article:published_time")

			if d is not None:
				lx = DateParser(str(d["content"]))
				if lx is not None:
					return(lx)
		return(None)
	except:
		print("ERROR for URL: " + line)

def extract(l):
	try:
		d = {}
		htmlcontent = urllib2.urlopen(line.strip()).read()
		d["url"] = line
		d["content"] = htmlcontent
		m = hashlib.md5()
		m.update(line.strip())
		filename = m.hexdigest()
		f = open("content1/" + filename + ".txt", "w+")
		json.dump(d, f)
		f.close()
	except:
		print("Error for URL: " + line)

#l = data.map(processor).collect()
#print("Length of l is: " + str(len(l)))

#years = []
#for x in l:
#	if x is not None and len(x) == 3:
#		years.append(x[0])

#plt.hist(years, 20)
#plt.show()

from random import shuffle

count = 0
f = open("remaining.txt", "r")
l = []
for line in f:
	l.append(str((line.strip())))

shuffle(l)

for line in l:
	extract(line)
	count = count + 1
	print(str(count) + "\n")

