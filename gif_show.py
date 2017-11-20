# -*- coding: utf-8 -*-
# !/usr/bin/env python

import asyncio
import hashlib
import inspect
from urllib.parse import unquote, urlencode

import request


class GifShow(request.Request):
    def __init__(self, client_key, sig_salt):
        super(GifShow, self).__init__()
        self.client_key = client_key
        self.sig_salt = sig_salt

    async def feeds(self, user_id, wait=5):
        url = 'http://api.gifshow.com/rest/n/feed/profile2'

        params = {
            'app': '0',
            'appver': '5.3.0.4846',
            'c': '360APP',
            'country_code': 'CN',
            'did': 'ANDROID_6c63242e7940d8ed',
            'language': 'zh-cn',
            'lat': '39.906215',
            'lon': '116.549291',
            'mod': '360(1605-A01)',
            'net': 'WIFI',
            'oc': 'UNKNOWN',
            'sys': 'ANDROID_6.0.1',
            'ud': '0',
            'ver': '5.3'
        }

        data = {
            'client_key': self.client_key,
            'count': 30,
            'lang': 'cn',
            'os': 'android',
            'privacy': 'public',
            'referer': 'ks://profile/144612798/-1/-1/8',
            'user_id': user_id
        }

        p_cursor = None

        page, feeds = 1, []
        while True:
            if p_cursor:
                data['pcursor'] = p_cursor

            data.pop('sig', None)
            data['sig'] = self.sig(params=params, data=data)

            self.logger.info(f'{inspect.currentframe().f_code.co_name} {page} {url} {params} {data}')

            results = await self.request(method='post', url=url, params=params, data=data, content='json')

            feeds.extend(results['feeds'])

            p_cursor = results['pcursor']
            if p_cursor == 'no_more':
                break

            page += 1
            await asyncio.sleep(wait)

        return feeds

    async def comments(self, user_id, photo_id, wait=5):
        url = 'http://api.gifshow.com/rest/photo/comment/list'

        params = {
            'app': '0',
            'appver': '5.3.0.4846',
            'c': '360APP',
            'country_code': 'CN',
            'did': 'ANDROID_6c63242e7940d8ed',
            'language': 'zh-cn',
            'lat': '39.912015',
            'lon': '116.554383',
            'mod': '360(1605-A01)',
            'net': 'WIFI',
            'oc': 'UNKNOWN',
            'sys': 'ANDROID_6.0.1',
            'ud': '0',
            'ver': '5.3'
        }

        data = {
            'client_key': self.client_key,
            'order': 'desc',
            'os': 'android',
            'photo_id': photo_id,
            'user_id': user_id
        }

        p_cursor = None

        page, comments = 1, []
        while True:
            if p_cursor:
                data['pcursor'] = p_cursor

            data.pop('sig', None)
            data['sig'] = self.sig(params=params, data=data)

            self.logger.info(f'{inspect.currentframe().f_code.co_name} {page} {url} {params} {data}')

            results = await self.request(method='post', url=url, params=params, data=data, content='json')

            comments.extend(results['comments'])

            p_cursor = results['pcursor']
            if p_cursor == 'no_more':
                break

            await asyncio.sleep(wait)

        page += 1
        return comments

    def sig(self, params, data):
        s = unquote('&'.join([urlencode(params), urlencode(data)]))
        s = ''.join(sorted(s.split('&'))) + self.sig_salt
        return hashlib.md5(s.encode()).hexdigest()


async def test():
    gif_show = GifShow(client_key='3c2cd3f3', sig_salt='382700b563f4')

    # feeds = await gif_show.feeds(user_id=144612798)
    # print(feeds)

    comments = await gif_show.comments(user_id=144612798, photo_id=3536580854)
    print(comments)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
