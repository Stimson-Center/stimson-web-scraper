# -*- coding: utf-8 -*-

__title__ = 'scraper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


class Video(object):
    """Video object
    """
    def __init__(self):
        # type of embed
        # embed, object, iframe
        self.embed_type = None
        # video provider name
        self.provider = None
        # width
        self.width = None
        # height
        self.height = None
        # embed code
        self.embed_code = None
        # src
        self.src = None
