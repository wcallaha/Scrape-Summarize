# Scrape websites and summarize them, opens file afterwards.


import requests
import subprocess
import webbrowser
import os

from bs4 import BeautifulSoup
from gensim.summarization import summarize, keywords
import wikipedia
import numpy as np
import spacy
# Use this to install en_core_web_sm:
	# https://spacy.io/usage/models

# File naming w. the date. 
import datetime
now = datetime.datetime.now()
nowf = now.strftime("%m-%d-%Y")




def Articles(url_list):
	###########
	# GET THE TEXT FROM THE ARTICLE AND CLEAN IT
	# retreive page text:

	ArticleDict = {}
	for url in url_list:
		page = requests.get(url).text
		soup = BeautifulSoup(page, features="lxml")

		# Find the headlines from the webpage.
		headline = soup.find('h1').get_text()

		# Find the paragraphs:
		p_tags = soup.find_all('p')

		# Get the text from each paragraph tags and strip surrounding whitepsace:
		p_tags_text = [tag.get_text().strip() for tag in p_tags]


		# Filter out sentences that contain newline chars or don't contain periods
		sentence_list = [s for s in p_tags_text if (not '\n' in s) and ('.' in s)]
		article = " ".join(sentence_list)

	#
	#############

		# SUMMARIZE!
		# Summarization is base on text ranking, from this paper: https://arxiv.org/pdf/1602.03606.pdf
		# Gives us a quarter-length summary
		summary = summarize(article, word_count = 275).split("\n")
		summary = " ". join(summary)
		ArticleDict[headline] = summary

	return ArticleDict

# This just works for NPR right now; different websites have different HTML formattings, 
# so getting the url out of the homepage might/will require a distinct function
def NPR():
	url = "https://npr.org"
	page = requests.get(url).text
	soup = BeautifulSoup(page, features = 'lxml')		
	arts = soup.find_all("article")

	# Scrape the first N articles
	article_count = 8

	# Empty list for content, links, and titles
	url_list = []

	# Get the links:
	for n in np.arange(0, article_count):
		link = arts[n].find('a')['href']
		url_list.append(link)

	ArticleDict = Articles(url_list)

	# Can either write to local text editor or html page (default is html)
	WriteHTML(ArticleDict)
	#WriteLocal(ArticleDict)

def WriteLocal(ArticleDict):
	name = "{}_Summary.txt".format(nowf)
	f = open(name, "w")

	for key, value in ArticleDict.items():
		f.write("################")
		f.write("\n")
		f.write(key)
		f.write("\n\n")
		f.write(value)
		f.write("\n\n")
	
	f.close()
	subprocess.Popen("{} {}".format("open", name), shell = True)	


def WriteHTML(ArticleDict):
	name = "{}_Summary.html".format(nowf)
	FILE = open(name, 'w')

	for key, value in ArticleDict.items():
		message = """<html>

		<font size = "6"> <head> %s </head> </font>

		<font size = "4"> <body><p> %s </p> </body> </font> 

		<html>""" %(key, value)

		FILE.write(message)

	FILE.close()

	path = os.path.abspath(name)
	filename = 'file://{}'.format(path)
	webbrowser.open_new_tab(filename)



NPR()
