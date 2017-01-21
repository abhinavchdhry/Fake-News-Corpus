#########################################
### Author: Abhinav Choudhury	     ####
### North Carolina State University  ####
### 2016			     ####
#########################################

import scrapy
import bs4
import re
import json

class OnionSpyder(scrapy.Spider):
	name = "OnionSpyder"
	start_urls = ['http://www.theonion.com/article/conservative-acquaintance-annoyingly-not-racist-35236']
	start_urls = start_urls + ['http://www.theonion.com/audio/georgia-legislature-bans-indoor-spitting-21000']
	start_urls = start_urls + ['http://www.theonion.com/article/manly-man-wastes-entire-years-worth-of-feelings-on-50209']
	start_urls = start_urls + ['http://www.theonion.com/article/millions-of-holiday-travelers-return-from-parents--37564']

	parsedArticleIDs = []
	processedArticleURLs = []
	writer = None
	dumpInitialized = 0

	def parse(self, response):
		parsed = bs4.BeautifulSoup(response.text, 'html.parser')
		d = {}
                actualURL = parsed.find("meta", property="og:url")["content"]
#                print("Current: " + actualURL)
		d["url"] = actualURL

		if actualURL != "" and actualURL not in self.processedArticleURLs and actualURL.split('/')[-2]=="article":
			title = parsed.find("meta", property="og:title")["content"]
#			print(title)
			d["title"] = title
			content_type = parsed.find("meta", property="og:type")["content"]
#			print(content_type)
			d["content_type"] = content_type
			published_time = parsed.find("meta", property="og:published_time")["content"]
#			print(published_time)
			d["published_time"] = published_time
			section = parsed.find("meta", property="og:section")["content"]
#			print(section)
			d["section"] = section
			text = parsed.find_all('div', class_='content-text')
			if (len(text) > 0 and text[0].p is not None):
				text = text[0].p.string
				d["text"] = text
#				print(text)

			# Dump to persistent storage here
#			if (self.writer is None):
#				self.writer = open("urls.txt", "w+")
#				if (self.writer is None):
#					print("Failed to open writer file")
#			self.writer.write(actualURL + "\n")
			self.processedArticleURLs.append(actualURL)

			if self.writer is None:
				self.writer = open("data.txt", "w+")
				json.dump(d, self.writer)
			else:
				self.writer.write("\n")
				json.dump(d, self.writer)

		# Redirect to next URL
		newURLs = []
		baseURL = "http://www.theonion.com"

		data = parsed.find_all("div", attrs={ "data-share-url": True})
		if (len(data) > 0):
			for element in data:
				if element["data-share-url"] not in newURLs:
					newURLs.append(element["data-share-url"])

		# <article class="summary" role="article"> filters
		otherArticles = parsed.find_all('article', class_="summary")
		print("OTHER ARTICLES, count = " + str(len(otherArticles)) + "\n\n")
		if len(otherArticles) > 0:
			for art in otherArticles:
#				print(art.a["data-track-label"])
#				print("\n\n")
				href = art.a["data-track-label"]
				urlTokens = href.split("/")
				if len(urlTokens) > 1 and urlTokens[1]=="article":
					url = baseURL + href
					if url not in newURLs:
						newURLs.append(url)

		# Return generator
		for url in newURLs:
			yield scrapy.Request(url, callback=self.parse)
