# -*- coding: utf-8 -*-
# Made by Thorsteinn Hjortur Jonsson with help from Petur Rafn Bryde
# Date of construction 29.08'15 - 31.08'15
import scrapy
import urlparse

# Here we define the fields for the spider items
from Verkefni1.items import KsiItem
# We need this to join the urls
from urlparse import urljoin
# My debugger - Must have!
import pdb

# Spider class derived from basic spider from the genspider command
class KsiSpiderSpider(scrapy.Spider):
    name = "playerspider"
    allowed_domains = ["ksi.is"]
    # This is the default base url - it will be overwritten if given a
    # custom url with the CrawlerWorker in main
    start_urls = [
           'http://www.ksi.is/mot/leikmenn/?felag=107&stada=0&kyn=%25&ArgangurFra=1980&ArgangurTil=1995'
    ]

    # This function parses through the list of players of given genders
    # of the given age span for the given teams. This information can be
    # read from the url given to parse.
    def parse(self, response):
        # Read through all rows in the table of class "alt"
        # This was discovered from playing with scrapy and reading the
        # page source of the www.ksi.is
        for sel in response.xpath('//tr[@class="alt"]'):
            # initalize the item
            item = KsiItem()
            # Fetch information about a player from table of players
            # Each player has its row, the names are kept in the /a
            # column and the year of birth is kept in the third column
            # utf-8 encoding must be ensure
            item['name'] = sel.xpath('td/a/text()')[0].extract().encode("utf-8")
            item['year'] = sel.xpath('td[3]/text()')[0].extract().encode("utf-8")
            # Fetch further information on the player from the url
            player_url = sel.xpath('td/a/@href').extract()[0]
            # This url gives the game data for the player, this was
            # discovered from reading the page source of the website
            # which hosts game data for each player.
            table_url = '&pListi=7&dFra-dd=31&dFra-mm=07&dFra-yy=1912&dTil-dd=30&dTil-mm=08&dTil-yy=2015'
            # join the game-data url with the base url
            url = response.urljoin(player_url + table_url)
            # Make a request to fetch data from the game-data website
            request = scrapy.Request(url, callback=self.parse_dir_contents)
            # To transfer the item to a new parsing function
            request.meta['item'] = item
            # return the item from the request and go to the next player
            yield request

    # This parse function parses the website which hosts all registered
    # games for a specific player. It returns a the field flokkur which
    # is a list of all the youth levels that the player has been
    # registered for.
    def parse_dir_contents(self, response):
        # necessary to fetch the item from the other parse method
        item = response.meta['item']
        # initialize an empty string and an empty list for conveniance
        temp_flokkur = ''
        flokkur = []
        # Boolean variables to prevent us from grabbing the duplicates
        f4 = False
        f3 = False
        f2 = False
        f1 = False
        # Goes through each row in the table and fetches all the
        # different youth levels that the player has been registered at
        for sel in response.xpath('//tr[@class="alt"]'):
            # The youth level data is stored in column two
            temp_flokkur = sel.xpath('td[2]/text()')[0].extract().encode("utf-8")
            # Sometimes the players have played for different teams at
            # the same youth level and the registration reflects that
            # Thus we just look for the substring 'x.' where x is the
            # corresponding number of the youth level.
            if f4 == False and temp_flokkur.find('4.') != -1:
                flokkur.append('4. flokkur')
                f4 = True
            elif f3 == False and temp_flokkur.find('3.') != -1:
                flokkur.append('3. flokkur')
                f3 = True
            elif f2 == False and temp_flokkur.find('2.') != -1:
                flokkur.append('2. flokkur')
                f2 = True
            elif f1 == False and temp_flokkur.find('Meistara') != -1:
                flokkur.append(u'Meistaraflokkur')
                f1 = True
        item['flokkur'] = flokkur
        yield item
