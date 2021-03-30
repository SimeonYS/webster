import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import WebsterItem
from itemloaders.processors import TakeFirst
import datetime
pattern = r'(\xa0)?'

class WebsterSpider(scrapy.Spider):
	name = 'webster'
	now = datetime.datetime.now()
	year = now.year

	start_urls = [f'https://webster.gcs-web.com/news-releases?a3ac091f_year%5Bvalue%5D={year}&op=Filter&a3ac091f_widget_id=a3ac091f&form_build_id=form-oV6MI1qjc_I3OHat0oQBKhxgk2W0voKbulDSrc7i2Zw&form_id=widget_form_base&page=0']

	def parse(self, response):
		post_links = response.xpath('//div[@class="nir-widget--field nir-widget--news--headline"]/a/@href').getall()
		post_links = [link for link in post_links if not 'static-files' in link]
		yield from response.follow_all(post_links, self.parse_post)

		next_button = response.xpath('//li[@class="pager__item pager__item--next"]/a/@href').get()
		if next_button:
			yield response.follow(next_button, self.parse)

		next_page = f'https://webster.gcs-web.com/news-releases?a3ac091f_year%5Bvalue%5D={self.year}&op=Filter&a3ac091f_widget_id=a3ac091f&form_build_id=form-oV6MI1qjc_I3OHat0oQBKhxgk2W0voKbulDSrc7i2Zw&form_id=widget_form_base&page=0'
		if self.year > 2013:
			self.year -= 1
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('(//div[@class="field__item"])[2]/text()').get().split(' at')[0]
		title = response.xpath('//div[@class="field__item"]/text()').get()
		content = response.xpath('//div[@class="xn-content"]//text()[not (ancestor::div[@class="ndq-table-responsive"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=WebsterItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
