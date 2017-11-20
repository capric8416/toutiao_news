# -*- coding: utf-8 -*-
# !/usr/bin/env python

import logging


def get_logger(name, level='INFO', fmt='%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s'):
    _level = getattr(logging, level)

    _logger = logging.getLogger(name=name)
    _logger.setLevel(_level)

    _stream_handler = logging.StreamHandler()
    _stream_handler.setLevel(_level)
    _stream_handler.setFormatter(logging.Formatter(fmt=fmt))
    _logger.addHandler(_stream_handler)

    return _logger