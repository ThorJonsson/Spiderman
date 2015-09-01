# -*- coding: utf-8 -*-
import scrapy
import urlparse

from Verkefni1.items import KsiItem
from urlparse import urljoin
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import pdb

class KsiSpiderSpider(scrapy.Spider):
    name = "playerspider"
    allowed_domains = ["ksi.is"]
    start_urls = [
           'http://www.ksi.is/mot/leikmenn/?felag=107&stada=0&kyn=%25&ArgangurFra=1980&ArgangurTil=1995'
    ]


    def parse(self, response):
        for sel in response.xpath('//tr[@class="alt"]'):
            item = KsiItem()
            # Fetch information about a player from table of players
            # Each player has its row
            item['name'] = sel.xpath('td/a/text()')[0].extract().encode("utf-8")
            item['year'] = sel.xpath('td[3]/text()')[0].extract().encode("utf-8")
            # Fetch further information on the player from the url
            player_url = sel.xpath('td/a/@href').extract()[0]
            # This url gives the game data for the player
            table_url = '&pListi=7&dFra-dd=31&dFra-mm=07&dFra-yy=1912&dTil-dd=30&dTil-mm=08&dTil-yy=2015'
            url = response.urljoin(player_url + table_url)
            request = scrapy.Request(url, callback=self.parse_dir_contents)
            request.meta['item'] = item
            yield request


    def parse_dir_contents(self, response):
        item = response.meta['item']
        temp_flokkur = ''
        flokkur = []
        f4 = 0
        f3 = 0
        f2 = 0
        f1 = 0
        for sel in response.xpath('//tr[@class="alt"]'):
            temp_flokkur = sel.xpath('td[2]/text()')[0].extract().encode("utf-8")
            if f4 == 0 and temp_flokkur.find('4.') != -1:
                flokkur.append('4. flokkur')
                f4 = 1
            elif f3 == 0 and temp_flokkur.find('3.') != -1:
                flokkur.append('3. flokkur')
                f3 = 1
            elif f2 == 0 and temp_flokkur.find('2.') != -1:
                flokkur.append('2. flokkur')
                f2 = 1
            elif f1 == 0 and temp_flokkur.find('Meistara') != -1:
                flokkur.append(u'Meistaraflokkur')
                f1 = 1

        item['flokkur'] = flokkur
        yield item
