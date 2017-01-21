#########################################
### Author: Abhinav Choudhury	     ####
### North Carolina State University  ####
### 2016			     ####
#########################################

import scrapy
import bs4
import re
import json

class NewsCrawler(scrapy.Spider):
	name = "RealNewsRightNow.com.Crawler"

	start_urls = ["http://realnewsrightnow.com/2016/06/cdc-cigarettes-tonic-water-may-help-prevent-spread-zika-virus/"]

	parsedArticleIDs = []
	processedArticleURLs = []
	writer = None
	dumpInitialized = 0
	paraLengthFilter = 20	# Use a length count of 20 words as filter to detect article paras in <p></p> blocks

	def parse(self, response):
		parsed = bs4.BeautifulSoup(response.text, 'html.parser')
		d = {}
                actualURL = parsed.find("meta", property="og:url")["content"]
		d["url"] = actualURL
		urlType = parsed.find("meta", property="og:type")["content"]

		if actualURL != "" and actualURL not in self.processedArticleURLs and urlType == "article":
			title = parsed.find("meta", property="og:title")["content"]
			d["title"] = title
			d["content_type"] = urlType
			desc = parsed.find("meta", property="og:description")["content"]
			d["desc"] = desc
			published_time = parsed.find("meta", property="article:published_time")["content"]
			d["published_time"] = published_time
			section = parsed.find("meta", property="article:section")["content"]
			d["section"] = section

			# Parse the text section here
			filteredParas = []
			allParas = parsed.findAll("p")
			for p in allParas:
				# Filter 1: Break out when artile author section reached
				if p.parent is not None and p.parent.name == 'div' and "class" in p.parent.attrs and 'author-content' in p.parent["class"]:
					break
				elif p.parent is not None and p.parent.name == 'div' and "class" in p.parent.attrs and 'comment-content' in p.parent["class"]:				# Filter 2: Cut out any comments encountered
					continue
				else:
					text = p.get_text()
					if text is not None:
						text = text.encode("ascii", 'ignore')
						paraLen = len(text.split())
						if paraLen > self.paraLengthFilter:
							filteredParas.append(text)
			
			d["text"] = '\n'.join(filteredParas)

			self.processedArticleURLs.append(actualURL)

			if self.writer is None:
				self.writer = open("../data/RNRNdata.txt", "w+")
				if d["text"] != "":
					json.dump(d, self.writer)
			else:
				self.writer.write("\n")
				if d["text"] != "":
					json.dump(d, self.writer)

		# Redirect to next list of URLs
		newURLs = []
		regex = "^http://realnewsrightnow.com/[0-9]{4}/[0-9]{2}/"
		r = re.compile(regex)
		hrefs = parsed.find_all('a', href=True)
		for hreftag in hrefs:
			href = hreftag["href"].encode('ascii', 'ignore')
			if (r.match(href) is not None):
				newURLs.append(href)

		# Return generator
		for url in newURLs:
			yield scrapy.Request(url, callback=self.parse)
