from __future__ import with_statement
import contextlib
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

import requests

from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import re
import multiprocessing as mp
from multiprocessing import Manager
import time


def make_tiny(url):
    request_url = ('http://tinyurl.com/api-create.php?' +
                   urlencode({'url': url}))
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode('utf-8')


class Keyword_search:
    def __init__(self, keyword):
        self.keyword = keyword

    def scrape(self):
        # 使用假header
        ua = generate_user_agent(os=('mac', 'linux'))
        headers = {'User-Agent': ua}

        response = requests.get(
            "https://ifoodie.tw/explore/list/" + self.keyword, headers=headers)

        soup = BeautifulSoup(response.text, "lxml")
        cards = soup.select("div.jsx-3440511973.restaurant-item", limit=10)

        manager = Manager()
        result = []

        for card in cards:
            content = manager.dict()

            def get_title(content):
                title = card.find(
                    "a", {"class": "jsx-3440511973 title-text"}).getText()
                title = title.replace('/', '-')
                content["title"] = title

            def get_address(content):
                try:
                    content["address"] = card.find(
                        "div", {"class": "jsx-3440511973 address-row"}).getText()
                except:
                    content["address"] = '未提供'

            def get_price(content):
                try:
                    string = re.findall('\$\d+(?:\.\d+)?', card.find(
                        "div", {"class": "jsx-3440511973 avg-price"}).getText())

                    content["price"] = string[0]

                except:
                    content["price"] = '未提供'

            def get_rate(content):
                try:
                    content["rate"] = card.find(
                        "div", {"class": "jsx-1207467136 text"}).getText()
                except:
                    content["rate"] = '未提供'

            def get_url(content):
                try:
                    url = card.find(
                        "a", {"class": "jsx-3440511973 click-tracker"})
                    content["url"] = make_tiny(
                        f'https://ifoodie.tw{url["href"]}')
                except:
                    content["url"] = 'https://google.com'

            def get_img_url(content):
                try:
                    img_url = card.select('img.jsx-3440511973.cover')
                    if img_url[0].get("data-src"):
                        content["img_url"] = make_tiny(
                            img_url[0]["data-src"])
                    else:
                        content["img_url"] = make_tiny(img_url[0]["src"])
                except:
                    content["img_url"] = 'https://i.imgur.com/bUTHY8X.jpg'

            p1 = mp.Process(target=get_title, args=(content,))
            p2 = mp.Process(target=get_address, args=(content,))
            p3 = mp.Process(target=get_price, args=(content,))
            p4 = mp.Process(target=get_rate, args=(content,))
            p5 = mp.Process(target=get_url, args=(content,))
            p6 = mp.Process(target=get_img_url, args=(content,))

            p1.start()
            p2.start()
            p3.start()
            p4.start()
            p5.start()
            p6.start()
            # Wait till they all finish and close them
            p1.join()
            p2.join()
            p3.join()
            p4.join()
            p5.join()
            p6.join()

            result.append(dict(content))

        return result
