# -*- coding: utf-8 -*-
# !/usr/bin/env python

import asyncio
import hashlib
import inspect
import math
import time

import execjs
from pyquery import PyQuery

import request


class Toutiao(request.Request):
    def __init__(self, user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 '
                                  '(KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'):
        super(Toutiao, self).__init__()

        self.user_agent = user_agent

        self.url_host = 'http://www.toutiao.com'
        self.url_user = f'{self.url_host}/c/user/'
        self.url_article = f'{self.url_host}/c/user/article/'
        self.url_content = f'{self.url_host}/item/'
        self.url_comments = f'{self.url_host}/api/comment/list/'
        self.url_search = f'{self.url_host}/search_content/'
        self.url_channel = f'{self.url_host}/api/pc/feed/'

    async def articles(self, user_id, page_type, wait=5):
        params = {
            'user_id': user_id,
            'page_type': page_type,  # 0: 视频, 1: 文章
            'max_behot_time': 0,
            'count': 20
        }

        page, data = 1, []
        while True:
            params.update(self.get_honey())

            self.logger.info(f'{inspect.currentframe().f_code.co_name} {page} {self.url_article} {params}')

            results = await self.request(
                url=self.url_article, params=params, refer=self.url_user + str(user_id) + '/', content='json')

            data.extend(results['data'])
            if not results['has_more']:
                break

            page += 1
            params['max_behot_time'] = results['next']['max_behot_time']

            await asyncio.sleep(wait)

        return data

    async def content(self, item_id):
        self.logger.info(f'{inspect.currentframe().f_code.co_name} {self.url_article} {item_id}')

        html = await self.request(url=self.url_content + str(item_id) + '/', content='text')

        p_tags = PyQuery(html)('script:contains(__ptags)').text()
        base_data = PyQuery(html)('script:contains(BASE_DATA)').text()

        return execjs.eval(''.join(['(function(){', p_tags, base_data, 'return BASE_DATA;})()']))

    async def comments(self, group_id, item_id, wait=5):
        params = {'group_id': group_id, 'item_id': item_id, 'offset': 0, 'count': 10}

        page, data = 1, []

        while True:
            params.update(self.get_honey())

            self.logger.info(f'{inspect.currentframe().f_code.co_name} {page} {self.url_comments} {params}')

            results = await self.request(url=self.url_comments, params=params, content='json')

            items = results['data']['comments']
            data.extend(items)
            if not results['data']['has_more']:
                break

            page += 1
            params['offset'] += len(items)

            await asyncio.sleep(wait)

        return data

    async def channels(self, category, wait=5):
        params = {
            'category': category,
            'max_behot_time': 0,
            'max_behot_time_tmp': 0,
            'tadrequire': 'true',
            'utm_source': 'toutiao',
            'widen': 1
        }

        page, data = 1, []

        while True:
            params.update(self.get_honey())

            self.logger.info(f'{inspect.currentframe().f_code.co_name} {page} {self.url_channel} {params}')

            results = await self.request(url=self.url_channel, params=params, content='json')

            items = results['data']
            if not items:
                break

            data.extend(items)

            page += 1
            params['max_behot_time'] = results['next']['max_behot_time']
            params['max_behot_time_tmp'] = results['next']['max_behot_time']

            await asyncio.sleep(wait)

        return data

    async def search(self, keyword, cur_tab, wait=5):
        params = {
            'autoload': 'true',
            'count': 20,
            'cur_tab': cur_tab,  # 1: 综合, 2: 视频, 3: 图集, 4: 用户, 5: 问答
            'format': 'json',
            'keyword': keyword,
            'offset': 0
        }

        page, data = 1, []

        while True:
            self.logger.info(f'{inspect.currentframe().f_code.co_name} {page} {self.url_search} {params}')

            results = await self.request(url=self.url_search, params=params, content='json')

            items = results['data']
            data.extend(items)
            if not results.get('has_more', 0):
                break

            page += 1
            params['offset'] += 20

            await asyncio.sleep(wait)

        return data

    def get_honey(self):
        _ = self

        timestamp = math.floor(time.time())
        hex_timestamp = hex(timestamp)[2:].upper()
        md5_timestamp = hashlib.md5(str(timestamp).encode()).hexdigest().upper()

        if len(hex_timestamp) != 8:
            return {
                'as': '479BB4B7254C150',
                'cp': '7E0AC8874BB0985'
            }

        first_5 = md5_timestamp[0: 5]
        last_5 = md5_timestamp[-5:]

        as_seed = ''.join([first_5[i] + hex_timestamp[i] for i in range(0, 5)])
        cp_seed = ''.join([hex_timestamp[j + 3] + last_5[j] for j in range(0, 5)])

        return {
            'as': ''.join(['A1', as_seed, hex_timestamp[-3:]]),
            'cp': ''.join([hex_timestamp[0: 3], cp_seed, 'E1'])
        }


async def test():
    toutiao = Toutiao()

    articles = await toutiao.articles(user_id=3877938770, page_type=1)
    print(articles)

    content = await toutiao.content(item_id=6436150901102084609)
    print(content)

    comments = await toutiao.comments(group_id=6476464650140516877, item_id=6476464650140516877)
    print(comments)

    results = await toutiao.search(keyword='悟空问答', cur_tab=4)
    print(results)

    results = await toutiao.channels(category='news_food')
    print(results)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
