#########################################
### Author: Abhinav Choudhury	     ####
### North Carolina State University  ####
### 2016			     ####
#########################################

import scrapy
import bs4
import re
import json

class EnduringVisionCrawler(scrapy.Spider):
	name = "enduringvision.com.Crawler"

	start_urls = ["http://www.enduringvision.com/news/world_061610.php"]
	start_urls += ["http://www.enduringvision.com/news/us.php", "http://www.enduringvision.com/news/world.php", "http://www.enduringvision.com/news/sports.php", "http://www.enduringvision.com/news/politics.php", "http://www.enduringvision.com/news/business.php", "http://www.enduringvision.com/news/science.php", "http://www.enduringvision.com/news/arts.php"]

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
       	                self.writer = open("../data/enduringvisiondata.txt", "w+")
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
		
		regex = "^http://www.enduringvision.com/news/[a-zA-Z]*_[0-9]*\.php$"
		r = re.compile(regex)
		r1 = re.compile("^[a-zA-z]*_[0-9]*\.php$")
		hrefs = parsed.find_all('a', href=True)
		for hreftag in hrefs:
			href = hreftag["href"].encode('ascii', 'ignore')
			if (r.match(href) is not None):
				if href not in self.processedArticleURLs:
					print("New URL: " + href)
					newURLs.append(href)
			elif (r1.match(href)):
				h = "http://www.enduringvision.com/news/" + href
				if h not in self.processedArticleURLs:
					newURLs.append(h)

		# Return generator
		for url in newURLs:
			yield scrapy.Request(url, callback=self.parse)
