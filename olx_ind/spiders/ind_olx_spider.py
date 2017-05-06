# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from PIL import Image
from io import BytesIO
import base64
from pytesseract import image_to_string


class IndOlxSpiderSpide(scrapy.Spider):
    name = "indspider"
    start_urls = ['http://olx.co.id/perlengkapan-bayi-anak/jakarta-dki/?view=list']

    def parse(self, response):
        script = """
                        function main(splash)
                          local url = splash.args.url
                          assert(splash:go(url))
                          assert(splash:wait(1))
                          assert(splash:runjs("$('.contactitem').click()"))
                          --assert(splash:runjs("$('.fnormal').click()"))
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
        item = dict()
        item['url'] = response.url
        item['item_name'] = response.xpath('//h1/text()').extract_first().strip()
        item['seller_name'] = response.xpath('(//span[contains(@class, "block color")])[1]/text()').extract_first()
        raw_image = response.xpath('//img[@class="contactimg"]/@src').extract_first()
        try:
            image = Image.open(BytesIO(base64.b64decode(raw_image.split(',')[1])))
            item['phone_number'] = image_to_string(image)
            yield item
        except Exception as e:
            self.logger.info('Got {} exeption on {} page'.format(e, response.url))
            pass

