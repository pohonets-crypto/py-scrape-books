from pathlib import Path
import re


import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"): # tag.class_name
            url = book.css("h3 a::attr(href)").get()
            yield response.follow(url, callback=self.parse_book)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response, **kwargs):
        title = response.css("div.product_main h1::text").get()
        price_text = response.css("p.price_color::text").get()
        if price_text:
            price = float(price_text.replace("£", ""))

        texts = response.css("p.instock.availability::text").getall()
        cleaned = " ".join(t.strip() for t in texts if t.strip())
        m = re.search(r"(\d+)\s+available", cleaned)
        amount_in_stock = int(m.group(1)) if m else None

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = rating_class.split()[-1] if rating_class else None

        crumbs = response.css("ul.breadcrumb li a::text").getall()
        category = crumbs[-1].strip()

        description = response.css("#product_description ~ p::text").get(default="").strip() # ~ - next to

        upc = response.css("table.table.table-striped tr:nth-child(1) td::text").get()
        # :nth-child(1) - first child element in parent container

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
