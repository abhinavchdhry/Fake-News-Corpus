from random import shuffle
import os
import json
import urllib2
import hashlib
import requests

f = open("combined.txt", "r")
all_urls = []
for line in f:
	all_urls.append(str(line.strip()))


done = []
for fi in os.listdir("./content/"):
	f1 = open("./content/" + fi, "r")
	for line in f1:
		d = json.loads(line)
		url = d["url"]
		done.append(str(url.strip()))
		break

remaining = list(set(all_urls) - set(done))
shuffle(remaining)
print("Remaining URL count: " + str(len(remaining)))

count = 0
for url in remaining:
	try:
		print(str(count+1) + ": Current URL: " + url)
#		content = urllib2.urlopen(url, timeout=3).read()
		content = requests.get(url).text.encode('ascii', 'ignore')
		d= {}
		d["url"] = url
		d["content"] = content
		m = hashlib.md5()
		m.update(url)
		filename = m.hexdigest()
		f2 = open("content/" + filename + ".txt", "w+")
		json.dump(d, f2)
		f2.close()
		count = count + 1
	except:
		print("ERROR!")
