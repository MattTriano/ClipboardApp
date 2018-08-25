# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from event import Event, EventFieldData
from categories import Category
from spider_base import SpiderBase

class HistorySpider(CrawlSpider, SpiderBase):
    name = 'history'
    allowed_domains = ['www.chicagohistory.org']

    rules = (
        Rule(LinkExtractor(restrict_css = '.title'), process_request = 'link_request', callback = 'parse_item'),
    )

    def __init__(self, start_date, end_date):
        CrawlSpider.__init__(self)
        SpiderBase.__init__(self, 'https://www.chicagohistory.org/', start_date, end_date, date_format = '%d %B %Y', request_date_format = '%Y%m%d')

    def start_requests(self):
        yield self.get_request('events', {
                'start_date': self.start_date,
                'end_date': self.end_date
            })
        

    def parse_start_url(self, response):
        def get_full_date(selector_result):
            result = []
            current_month = ''
            for text in selector_result:
                # Month names are all greater than 2 characters
                # Days of the month are all 2 characters or fewer
                if len(text) > 2:
                    current_month = text
                else:
                    result.append(f'{text} {current_month}')
            return result

        # parser = EventParser(response, 'Chicago History Museum')
        # parser.extract('a.title').save('title')
        # parser.extract('a.title::attr(href)').save('url')
        # parser.extract('.time').save('time_range')
        # parser.extract('.xcalendar-row .number,.month', get_full_date).save('date')
        # parser.extract('.info').save('description')

        parser = self.create_parser(response)
        titles = parser.parse('title', 'a.title')
        urls = parser.parse('url', 'a.title', extract_func=lambda i: i.attr('href'))
        times = parser.parse('time_range', '.time', iter_children=True)
        dates = parser.parse('date', '.xcalendar-row .number,.month', transform_func=get_full_date, iter_children=True)
        descriptions = parser.parse('description', '.info', iter_children=True)

        return self.create_events('Chicago History Museum', titles, descriptions, urls, times, dates)

        #return parser.create_events()

        # def get_full_date(xpath_result):
        #     result = []
        #     current_month = ''
        #     for text in xpath_result.data:
        #         # Month names are all greater than 2 characters
        #         # Days of the month are all 2 characters or fewer
        #         if len(text) > 2:
        #             current_month = text
        #         else:
        #             result.append(f'{text} {current_month}')
        #     return EventFieldData(xpath_result.item, result)

        # titles = self.extract('title', response.css, 'a.title::text')
        # urls = self.extract('url', response.css, 'a.title::attr(href)')
        # times = self.extract('time_range', response.css, '.time').remove_html()
        # dates = get_full_date(self.extract('date', response.css, '.xcalendar-row .number,.month').remove_html())
        # descriptions = self.extract('description', response.css, '.info').remove_html()

        # return self.create_events('Chicago History Museum', titles, descriptions, urls, times, dates)

    def link_request(self, request):
        # Store the original url in case it gets redirected later
        request.meta['clicked_url'] = request.url
        return request

    def parse_item(self, response):
        parser = self.create_parser(response)
        address = parser.extract('//h3[contains(text(), "Event Location")]/following-sibling::div/p').result()
        price = parser.extract('.price').result()
        [i.text() for i in pq('.details-box h3:contains("Event Location")').siblings('.row').items()]
        return Event(url=response.meta['clicked_url'], address=address, price=price[0] if len(price) > 0 else '0')

        location = self.extract('location', response.xpath, '//h3[contains(text(), "Event Location")]/following-sibling::div/p').remove_html()
        price = self.extract('price', response.css, '.price').remove_html(True)

        return Event(
            url = response.meta['clicked_url'],
            address = location.data,
            price = price.data[0] if len(price.data) > 0 else '0'
        )