import scrapy

# Titulo de la web = //h1/a/text()
# Citas = //span[@class ="text" and @itemprop = "text"]/text()
# Top ten tags = //div[contains(@class, 'tags-box')]//a[contains(@class, 'tag')]/text()
# Next page button = //ul[@class="pager"]//li[@class="next"]/a/@href
# Author = //div[@class="quote"]//small[@class="author"]/text()

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'https://quotes.toscrape.com/'
    ]
    custom_settings = {
        'FEED_URI': 'quotes.json',
        'FEED_FORMAT': 'json',
        'CONCURRENT_REQUESTS': 24,
        'MEMUSAGE_LIMIT_MB': 2048,
        'MEMUSAGE_NOTIFY_MAIL': ['pedro.espinoza.c@uni.pe'],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'PepitoMartinez',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def parse_only_quotes(self, response, **kwargs):
        if kwargs:
            quotes = kwargs['quotes']
            author = kwargs['author']
        quotes.extend(response.xpath('//span[@class ="text" and @itemprop = "text"]/text()').getall())
        author.extend(response.xpath('//div[@class="quote"]//small[@class="author"]/text()').getall())
                
        next_page_button_link = response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback = self.parse_only_quotes, cb_kwargs = {'quotes': quotes, 'author': author})
        else:
            yield {
                'quotes': [quote + ' by ' + author for quote, author in zip(quotes, author)]
            }
            # i = 0
            # quotes_author =[]
            # for i in range(len(quotes)):
            #     quotes_author.append(quotes[i])
            #     quotes_author.append(author[i])
            
            # yield{
            #     'quotes': quotes_author
            # }

    def parse(self, response):
        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//span[@class ="text" and @itemprop = "text"]/text()').getall()
        top_tags = response.xpath('//div[contains(@class, "tags-box")]//a[contains(@class, "tag")]/text()').getall()
        author = response.xpath('//div[@class="quote"]//small[@class="author"]/text()').getall()

        top = getattr(self, 'top', None)
        if top:
            top = int(top)
            top_tags = top_tags[:top]

        yield {
            'title': title,
            'top_tags': top_tags
        }

        next_page_button_link = response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback = self.parse_only_quotes, cb_kwargs = {'quotes': quotes, 'author': author})

