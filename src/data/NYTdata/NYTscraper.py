import requests, json
from bs4 import BeautifulSoup as bs
from nytimesarticle import articleAPI
import random, time

#api = articleAPI("1365a8efa2ee4cd9bb685612a03904b1")
#api = articleAPI("aeff1d6a957f40c19bbda08b9714c4a4")
#api = articleAPI("336886d72ea14a71a9a5c34800f9a761")
api =  articleAPI("8b80d00bbc10401aa74b05e4be7fd065")

#api =  articleAPI("4009c64cd2cf4a6ea25592535e9c83e3")
#api =  articleAPI("a91daaccbde54672921fcd3742a1a85d")
#api =  articleAPI("8b3df0ca99ed46d6bbf103c934c94ce9")
#api = articleAPI("c159e3dfabdc45c993619e1bb6425002")

#api = articleAPI("98ebc312f98d4257b1c27445152e6435")
#api = articleAPI("9555d8d40c0044659546fdeeda4d290e")
#api = articleAPI("3f94c1e436964be6909319b6d0989ec9")

#api = articleAPI("7b3f3b398aec414aae09501f8c430155")
#api = articleAPI("c1083f7480f941159de8f70d60975715")
#api = articleAPI("bf53fb1b8c144020b41bbdf99b676157")
#api = articleAPI("ade519c504884db097f6ce8fe9aecc2b")

#api = articleAPI("4e3304e9ba354531ba8f35935a21188b")

month = 9
outfile = open("NYTstories_" + str(month) + ".dat", "a")

## Algorithm
# Randomly sample 1000 articles per month from the monthly data
# Get total number of articles per month
# Generate random 1000 indices

stories = []

# Loop over month number
if 1:
	print("## Current month: " + str(month))
	dates = [20160000 + month*100 + day for day in xrange(12, 32)]

	# For each date in the month
	processed = 0
	failed = 0
	for date in dates:
		try:
			count = api.search(fq = {'source':['The New York Times']}, begin_date = date, end_date = date)
			if 'response' not in count:
				time.sleep(1)
				count = api.search(fq = {'source':['The New York Times']}, begin_date = date, end_date = date)
		except:
			print("Exeption!")
			continue

		count = count['response']
		count = count['meta']
		count = count['hits']

		print("Current date: " + str(date))
		idxs = random.sample(xrange(count), min(50, count))
		time.sleep(1)
		for idx in idxs:
			pageno = idx/10
			idx_in_page = idx%10
			try:
				res = api.search(fq = {'source':['The New York Times']}, begin_date = date, end_date = date, page=str(pageno))
#	print("End: " + str(end_date))
				if 'response' not in res:
					time.sleep(1)
					res = api.search(fq = {'source':['The New York Times']}, begin_date = date, end_date = date, page=str(pageno))
			except:
				print("Exception!")
				continue
			res = res['response']
			docs = res['docs']
			url = docs[idx_in_page]["web_url"]
			r = requests.get(url)
			if r.status_code == 200:
				parsed = bs(r.text, "html.parser")
				paras = parsed.findAll("p")
				story_body = []
				for para in paras:
					if 'class' in para.attrs and 'story-body-text' in para['class']:
						story_body.append(para.get_text().strip().encode('ascii', 'ignore'))
				story = "".join(story_body)
				if story != "" and len(story.split(" ")) >= 100:
					stories.append("".join(story))
					json.dump({"text":"".join(story_body)}, outfile)
					outfile.write("\n")
					outfile.flush()
					processed += 1
				else:
					failed += 1
			else:
				failed += 1
				print("## Status_code: " + str(r.status_code) + " URL: " + url)
			print("## Processed: " + str(processed) + ", failed: " + str(failed))

print("## Total stories collected: " + str(len(stories)))

print("## Writing to file...")
json.dump(stories, "NYTstories.json")
