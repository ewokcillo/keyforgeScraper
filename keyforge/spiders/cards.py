# -*- coding: utf-8 -*-
import pymongo
import scrapy
from scrapy import Request

import json
import urllib.parse as urlparse

import keyforge.settings


PAGE_SIZE = 10
PAGE_URL = ("https://www.keyforgegame.com/api/decks/?"
            "page={}&page_size=10&search=&power_level=0,11"
            "&chains=0,24&ordering=date")
DECK_URL = 'https://www.keyforgegame.com/api/decks/{}/?links=cards,notes'


def get_first_page():
    mongo_uri = keyforge.settings.MONGO_URI,
    mongo_db = keyforge.settings.MONGO_DATABASE
    client = pymongo.MongoClient(mongo_uri)
    db = client[mongo_db]
    page = int(db['decks'].count()/PAGE_SIZE) - 1

    return page if page > 0 else 1


class CardsSpider(scrapy.Spider):
    name = 'cards'
    allowed_domains = ['keyforgegame.com']
    start_urls = [PAGE_URL.format(get_first_page(), PAGE_SIZE)]

    def parse(self, response):
        page = int(urlparse.parse_qs(response.url.split('?')[-1])['page'][-1])
        page_json = json.loads(response.body)

        if page != page_json['count']:
            yield Request(PAGE_URL.format(page+1, PAGE_SIZE))

        for deck in page_json['data']:
            deck['collection'] = 'decks'
            yield deck
            yield Request(DECK_URL.format(deck['id']),
                          callback=self.parse_deck)

    def parse_deck(self, response):
        deck_json = json.loads(response.body)
        for card in deck_json['_linked']['cards']:
            card['collection'] = 'cards'
            yield card
