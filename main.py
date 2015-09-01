#!/usr/bin/python
# -*- coding: utf-8 -*-
# Made by Thorsteinn Hjortur Jonsson with help from Petur Rafn Bryde
# Date of construction: 29.09'15 - 31.09'15
# Looks at the volume of players playing at different youth levels for
# teams in Knattspyrnusamband Islands
# Only checks players age 18 or older who have played at least one game in "meistaraflokkur"

from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.xlib.pydispatch import dispatcher

from datetime import date
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import pdb

# This class does some magic discovered by Petur.
# It's a framework that allows us to initialize the spider as a function
# call.
class CrawlerWorker():
    # If there are no custom urls, we use the one defined in the spider
	def __init__(self, spider_name, custom_start_urls = None):

		self.items = [] # data to return

		self.settings = get_project_settings()
		self.process = CrawlerProcess(self.settings)
		self.process.crawl(spider_name, start_urls = custom_start_urls)
		dispatcher.connect(self.add_item, signals.item_passed)

	def add_item(self, item):
		self.items.append(item)


	def run(self):
		self.process.start() # the script will block here until the crawling is finished



def get_team_data(team_code, gender, min_age=18):
	# crawls ksi.is and finds the the number of registered matches at
	# each youth level (level 4,3 and 2)
	# returns a vector of ints

	# team_code: string, e.g. KR: 107
	# gender: string, 'male', 'female' or 'both'
	# min_age: int, e.g. 18

	start_url_base = "http://www.ksi.is/mot/leikmenn/?"
	start_url_team = "felag=" + team_code				# add area code
	start_url_status= "&stada=1"			# players = 1, other = 2

	if gender == "male":
		start_url_gender = "&kyn=1"
	elif gender == "female":
		start_url_gender = "&kyn=2"
	else:
		start_url_gender = "&kyn=%25"                   # both genders

    # We only look at players that have reach a certain age today, but
    # we look as far back as possible.

	start_url_years = ("&ArgangurFra=1900&ArgangurTil=" +
				str(date.today().year - min_age) )
	start_url = start_url_base + start_url_team + start_url_status + start_url_gender + start_url_years
	start_urls = [start_url]

	player_age_worker = CrawlerWorker('playerspider', custom_start_urls = start_urls)
	player_age_worker.run()
        return player_age_worker.items


if __name__ == "__main__":


	# ignores players whose last game was more than max_years_since_game years ago
	# ignores players born later than minimum_age

	# parameters:
	teams = {'KR': '900'}
        # Start the spider
	KRitem = get_team_data(teams['KR'], gender = 'other')
	# We list all the youth divisions as we iterate through each
	# player. Then we make a histogram of the frequencies for each
	# youth level.
	flokkur_list = []
	temp_player = 'name'
	for player in KRitem:
            # We say that a player has gone through the youth ranks if
            # it has ever been registered for the team in the youth
            # ranks, otherwise if he has only games for the first team
            # then we say that he is bought.
            uppalinn = False
	    print player
            if '4. flokkur' in player['flokkur']:
                flokkur_list.append('4. flokkur')
                uppalinn = True
            if '3. flokkur' in player['flokkur']:
                flokkur_list.append('3. flokkur')
                uppalinn = True
            if '2. flokkur' in player['flokkur']:
                flokkur_list.append('2. flokkur')
                uppalinn = True
            if 'Meistaraflokkur' in player['flokkur'] and uppalinn:
                flokkur_list.append('Meistaraflokkur - uppalinn')
            elif 'Meistaraflokkur' in player['flokkur']:
                flokkur_list.append(u'Meistaraflokkur - aðkeyptur')

        # The counter registers the frequencies for different youth
        # levels.
        cnt = Counter(flokkur_list)
        flokkur_names = cnt.keys()
        flokkur_counts = cnt.values()
        # Plot histogram using matplotlib bar().
        indexes = np.arange(len(flokkur_names))
        width = 0.3
        plt.bar(indexes, flokkur_counts, width)
        plt.xticks(indexes + width * 0.5, flokkur_names)
        plt.ylabel('Number of players')
        plt.title(u'Number of players in different ranks - ÍBV')
        plt.show()


