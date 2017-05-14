# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from olx_ind.items import OlxIndItem
from PIL import Image
from io import BytesIO
import base64
from pytesseract import image_to_string


class OlxIndSpider(scrapy.Spider):
    name = "olxindspider"

    def start_requests(self):
        url = 'http://olx.co.id/perlengkapan-bayi-anak/jakarta-dki/?view=list&page={}'
        # Make request to a first 10 pages
        for i in range(1, 11):
            yield self.make_requests_from_url(url.format(i))

    def parse(self, response):
        script = """
                        function main(splash)
                          local url = splash.args.url
                          assert(splash:go(url))
                          assert(splash:wait(1))
                          assert(splash:runjs("$('.contactitem').click()"))
                          assert(splash:wait(1))
                          return {
                            html = splash:html()
                          }
                        end
                        """
        for link in response.xpath('//h3/a/@href').extract():
            yield SplashRequest(link, callback=self.parse_phone, endpoint='execute',
                                args={'lua_source': script})

    def parse_phone(self, response):
        item = OlxIndItem()
        item['url'] = response.url
        item['item_name'] = response.xpath('//h1/text()').extract_first().strip()
        item['seller_name'] = response.xpath('(//span[contains(@class, "block color")])[1]/text()').extract_first()
        raw_image = response.xpath('//img[@class="contactimg"]/@src').extract_first()
        try:
            image = Image.open(BytesIO(base64.b64decode(raw_image.split(',')[1])))
            item['phone_number'] = ''.join(image_to_string(image).split())
            yield item
        except Exception as e:
            self.logger.info('Exeption {} on {} page'.format(e, response.url))
            pass
