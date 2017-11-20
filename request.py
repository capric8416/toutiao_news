# -*- coding: utf-8 -*-
# !/usr/bin/env python

import asyncio

import aiohttp

import logger


class Request(object):
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.logger = logger.get_logger(self.__class__.__name__)

    async def request(self, method='get', retries=10, timeout=10, wait=3, refer='', content='text', *args, **kwargs):
        r = getattr(self.session, method)

        headers = {}
        if refer:
            headers['Referer'] = refer

        for _ in range(retries):
            try:
                async with r(timeout=timeout, headers=headers, *args, **kwargs) as resp:
                    if content == 'binary':
                        return await resp.content.read()
                    return await getattr(resp, content)()
            except Exception as e:
                self.logger.exception(e)
                await asyncio.sleep(wait)

    def __del__(self):
        self.session.close()
