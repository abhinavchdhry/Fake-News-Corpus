import os
import json
from bs4 import BeautifulSoup as bs
import sys

fake_dir = "./content/"
real_dir = "./guardian/"

# List of feature extraction routines
# Each article webpage (HTML) is passed through each of these routines
# It is the responsibility of the routine to add its extracted feature to the feature dictionary passed to it
# Routines must have the signature extractor_routine(html, inFeatureDict)
extractor_routines = []

def text_extractor(html, feature_dict):
	parsed = bs(html, "html.parser")
	allParas = parsed.findAll("p")
	filteredParas = []
	for p in allParas:
		if p.parent is not None and p.parent.name == 'div' and "class" in p.parent.attrs and \
			'author-content' in p.parent["class"]:
			break
		elif len(p.findAll('script')) > 0:
			continue
		elif p.parent is not None and p.parent.name == 'div' and "class" in p.parent.attrs and \
			('comment-content' in p.parent["class"] or 'reply' in p.parent["class"]):
			continue
		else:
			text = p.get_text()
			if text is not None:
				if u'\xa0' in text:
					text = text.replace(u'\xa0', u' ')
				text = text.encode("ascii", "ignore").strip()
				paraLen = len(text.split())
				if paraLen > 20:
					filteredParas.append(text)
	text = "\n".join(filteredParas).strip()
	if (text.strip() != ""):
		feature_dict["text"] = text

extractor_routines.append(text_extractor)

count = 1
size = len(os.listdir(fake_dir))

l = []
for a in os.listdir(fake_dir):
	print("Fake " + str(count) + " of " + str(size) + ": " + a + " Current memory: " + str(sys.getsizeof(l)))
	f = open(fake_dir + a, "r")
	d = None
	for line in f:
		d = json.loads(line)
		break
	html = d["content"]
	feature_dict = {}
	for extract_feature in extractor_routines:
		extract_feature(html, feature_dict)
	if ("text" in feature_dict):
		feature_dict["class"] = "Fake"
		f.close()
		l.append(feature_dict)
	count += 1

count = 1
size = len(os.listdir(real_dir))

for a in os.listdir(real_dir):
	print("Real " + str(count) + " of " + str(size) + ": " + a + " Current memory: " + str(sys.getsizeof(l)))
	f = open(real_dir + a, "r")
	d = None
	for line in f:
		d = json.loads(line)
		break
	html = d["content"]
	feature_dict = {}
	for extract_feature in extractor_routines:
		extract_feature(html, feature_dict)
	if "text" in feature_dict:
		feature_dict["class"] = "Real"
		f.close()
		l.append(feature_dict)
	count += 1

print("Writing to file...\n")
out = open("data.json", "w")
json.dump(l, out)
out.close()

