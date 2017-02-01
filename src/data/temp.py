import requests
import json
import re
import os
from bs4 import BeautifulSoup as bs

f1 = open("allLines.txt", "w+")

for f in os.listdir("content/"):
	print(f)
	f2 = open("content/" + f, "r")
	for line in f2:
		d = json.loads(line.strip())
		parsed = bs(d["content"], "html.parser")
		f1.write(d["url"] + "\n")
		p = parsed.find_all("p")
		if p is not None:
			l = []
			for p1 in p:
				if len(p1.attrs) == 0:
					if p1.parent is not None and p1.parent.name == 'div' and 'class' in p1.parent.attrs.keys() and 'comment-content' in p1.parent['class']:
						continue
					else:
						if len(p1.get_text().strip().encode('ascii', 'ignore').split()) > 20:
							text = p1.get_text().encode('ascii', 'ignore')
							l.append(text)
			t = " ".join(l)
			f1.write(t + "\n\n\n")
