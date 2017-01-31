#########################################
### Author: Abhinav Choudhury	     ####
### North Carolina State University  ####
### 2017			     ####
#########################################

import scrapy
import bs4
import re
import json

class NewsbiscuitCrawler(scrapy.Spider):
	name = "newsbiscuit.com.Crawler"
	filename = "../data/newsbiscuit.com.data"

	start_urls = ["http://www.newsbiscuit.com/2017/01/25/trump-declares-obama-presidency-was-just-fake-news/"]
	start_urls += ["http://www.newsbiscuit.com"]

	parsedArticleIDs = []
	processedArticleURLs = []
	writer = None
	dumpInitialized = 0
	paraLengthFilter = 20	# Use a length count of 20 words as filter to detect article paras in <p></p> blocks

	def parse(self, response):
		parsed = bs4.BeautifulSoup(response.text, 'html.parser')
		pageType = parsed.find('meta', property="og:type")
		if pageType is not None:
			pageType = pageType["content"]
		pageTitle = parsed.find('meta', property="og:title")
		pageDesc = parsed.find('meta', property="og:description")
		pageURL = parsed.find('meta', property="og:url")
		pageDateTime = parsed.find('meta', property="article:published_time")
		articleSection = parsed.find('meta', property="article:section")
		allParas = parsed.find_all("p")
                text = []
		if allParas is not None:
                        for para in allParas:
                                if para is not None:
					pa = para.get_text()
					if pa is not None and pa.strip() != "":
                                        	text.append(pa.strip().encode('ascii', 'ignore'))


		if None not in [pageType, pageTitle, pageDesc, pageURL, pageDateTime, articleSection] and pageType == "article" and len(text) > 0:
			d = {}
			d["url"] = pageURL["content"]
			d["type"] = "article"
			d["section"] = articleSection
			d["text"] = "\n".join(text)
			d["published_date"] = pageDateTime["content"]
			d["title"] = pageTitle["content"]
			d["desc"] = pageDesc["content"]

		if self.writer is None:
       	                self.writer = open(self.filename, "w+")
#                              	if d["text"] != "":
#                               		json.dump(d, self.writer)
			self.writer.write(response.url)
               	else:
                     	self.writer.write("\n")
#                                if d["text"] != "":
#                                	json.dump(d, self.writer)
			self.writer.write(response.url)

		self.processedArticleURLs.append(response.url)
		
		# Redirect to next list of URLs
		newURLs = []
		
		regex = "^http://www.newsbiscuit.com/[0-9]{4}/[0-9]{2}/[0-9]{2}/[a-zA-Z0-9]*\-[a-zA-Z0-9\-]*/$"
		r = re.compile(regex)
		hrefs = parsed.find_all('a', href=True)
		for hreftag in hrefs:
			href = hreftag["href"].encode('ascii', 'ignore')
			if (r.match(href) is not None and href not in self.processedArticleURLs):
				print("New URL: " + href)
				newURLs.append(href)

		# Return generator
		for url in newURLs:
			yield scrapy.Request(url, callback=self.parse)
