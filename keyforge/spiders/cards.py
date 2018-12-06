# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

import json
import urllib.parse as urlparse

PAGE_SIZE = 10
PAGE_URL = ("https://www.keyforgegame.com/api/decks/?"
            "page={}&page_size=10&search=&power_level=0,11"
            "&chains=0,24&ordering=-date")
DECK_URL = 'https://www.keyforgegame.com/api/decks/{}/?links=cards,notes'


class CardsSpider(scrapy.Spider):
    name = 'cards'
    allowed_domains = ['keyforgegame.com']
    start_urls = [PAGE_URL.format(1, PAGE_SIZE)]

    def parse(self, response):
        page = urlparse.parse_qs(response.url.split('?')[-1])['page'][-1]
        page_json = json.loads(response.body)

        count = 2
        while page != page_json['count']:
            yield Request(PAGE_URL.format(count, PAGE_SIZE))

            for deck in page_json['data']:
                yield Request(DECK_URL.format(deck['id']),
                              callback=self.parse_deck)
            count += 1

    def parse_deck(self, response):
        deck_json = json.loads(response.body)
        for card in deck_json['_linked']['cards']:
            yield card
