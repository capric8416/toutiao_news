# -*- coding: utf-8 -*-
# !/usr/bin/env python

import asyncio

import execjs
import lxml.html
from pyquery import PyQuery

import request


class WeChat(request.Request):
    def __init__(self):
        super(WeChat, self).__init__()

        self.url_search = 'http://weixin.sogou.com/weixin'

    async def search(self, type_, query, wait=5):
        params = {
            'ie': 'utf8',
            'type': type_,  # 1: 公众号, 2: 文章
            'query': query
        }

        html = await self.request(url=self.url_search, params=params)

        data = []

        pq = PyQuery(html)
        data.extend(self._search(pq=pq))

        while True:
            next_page = pq('#pagebar_container #sogou_next').attr('href')
            if not next_page:
                break

            await asyncio.sleep(wait)

            html = await self.request(url=self.url_search + next_page)
            pq = PyQuery(html)
            data.extend(self._search(pq=pq))

        return data

    async def articles(self, url, wechat_id):
        html = await self.request(url=url)
        script = PyQuery(html)(f'script:contains({wechat_id})')
        return execjs.eval(''.join(['(function(){', script.split('\n')[-2], 'return msgList;})()']))

    async def content(self, url):
        url = 'https://mp.weixin.qq.com' + url
        text = await self.request(url=url)

        # img_urls = [img.attr('data-src') or img.attr('src') for img in PyQuery('#page-content img').items()]
        # img_urls = [src for src in img_urls if src]
        # img_content = await asyncio.gather(*[self._img(src=src) for src in img_urls])

        doc = lxml.html.document_fromstring(text)
        for img in doc.xpath('//div[@id="page-content"]//img'):
            src = img.attrib.get('data-src', '')
            if src:
                img.attrib['src'] = src
                img.attrib['data-src'] = ''

        return lxml.html.tostring(doc).decode()

    def _search(self, pq):
        items = []

        for li in pq('.news-list2 li').items():
            txt_box = li('.gzh-box2 .txt-box')
            account_image = li('.img-box a[uigs*=account_image]')

            item = {
                'wechat_id': txt_box('.info label[name*=weixinhao]').text(),
                'name': self._text(pq=txt_box('.tit a[uigs*=account_name]')),
                'image': account_image('img').attr('src'),
                'qrcode': li('.ew-pop .pop img').attr('src'),
                'intro': self._text(pq=li('dl:eq(0) dd')),
                'auth': self._text(pq=li('dl:eq(1) dd')),
                'url': account_image.attr('href'),
            }

            item['open_id'] = item['image'].rpartition('/')[-1]
            if 'document.write' in item['auth']:
                item['auth'] = ''

            items.append(item)

        return items

    def _text(self, pq):
        _ = self

        if pq.outer_html() is None:
            return ''
        return ''.join(lxml.html.document_fromstring(pq.outer_html()).xpath('descendant-or-self::*/text()')).strip()

    async def _img(self, src):
        return src, await self.request(url=src, content='binary')


async def test():
    w = WeChat()

    # accounts = await w.search(type=1, query='汉川网')
    # print(accounts)
    #
    # articles = await w.articles(url='http://mp.weixin.qq.com/profile?src=3&timestamp=1508058581&ver=1&signature=JNcPusIDwZEG*kniKrExtY92SEnvPZYRib2xwKyuWTwrz9Ko*C8wGJR0mnJdIVUNrvjUGMiEVVJ0in28HYVaCw==')
    # print(articles)

    content = await w.content(
        url='/s?timestamp=1508061795&src=3&ver=1&signature=adF8uu7ImlxdJavPRlqVi4K4HnIZFjiifhXN4TtTapiIQLka9gy4vLq0qHB3am2CTVq4g5g*g8pmaNKmEJsuKC0uSADSVhG8hkBYak0ampatj*oluWY0tUUMmD8w8KZrBv3vmQL6ORgiq5KSepTkro-FjpLx*epA8k1CpZ4iFnE=')
    print(content)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
