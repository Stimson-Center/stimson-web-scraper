# -*- coding: utf-8 -*-
"""
Newspaper uses a lot of python-goose's parsing code. View theirlicense:
https://github.com/codelucas/newspaper/blob/master/GOOSE-LICENSE.txt

Parser objects will only contain operations that manipulate
or query an lxml or soup dom object generated from an article's html.
"""
import logging
import re
import string

from copy import deepcopy
from html import unescape

import lxml.etree
import lxml.html
import lxml.html.clean
from bs4 import BeautifulSoup, UnicodeDammit, NavigableString

from .utils import innerTrim

log = logging.getLogger(__name__)

allow_tags = [
    'a', 'span', 'p', 'br', 'strong', 'b',
    'em', 'i', 'tt', 'code', 'pre', 'blockquote', 'img', 'h1',
    'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd'
]

class Parser(object):

    @classmethod
    def xpath_re(cls, node, expression):
        regexp_namespace = "http://exslt.org/regular-expressions"
        items = node.xpath(expression, namespaces={'re': regexp_namespace})
        return items

    @classmethod
    def drop_tag(cls, nodes):
        if isinstance(nodes, list):
            for node in nodes:
                node.drop_tag()
        else:
            nodes.drop_tag()

    @classmethod
    def css_select(cls, node, selector):
        return node.cssselect(selector)

    @classmethod
    def get_unicode_html(cls, html):
        if isinstance(html, str):
            return html
        if not html:
            return html
        converted = UnicodeDammit(html, is_html=True)
        if not converted.unicode_markup:
            raise Exception(
                'Failed to detect encoding of article HTML, tried: %s' %
                ', '.join(converted.tried_encodings))
        html = converted.unicode_markup
        return html

    @classmethod
    def from_string(cls, html):
        html = cls.get_unicode_html(html)
        # Enclosed in a `try` to prevent bringing the entire library
        # down due to one article (out of potentially many in a `Source`)
        # noinspection PyBroadException,PyUnusedLocal
        # lxml does not play well with <? ?> encoding tags
        if html.startswith('<?'):
            html = re.sub(r'^<\?.*?\?>', '', html, flags=re.DOTALL)
        cls.doc = lxml.html.fromstring(html)
        return cls.doc

    @classmethod
    def clean_article_html(cls, node):
        global allow_tags
        article_cleaner = lxml.html.clean.Cleaner()
        article_cleaner.javascript = True
        article_cleaner.style = True
        article_cleaner.allow_tags = allow_tags
        article_cleaner.remove_unknown_tags = False
        return article_cleaner.clean_html(node)

    # @classmethod
    # def soup_strip_tags(cls, html, allow_tags):
    #     soup = BeautifulSoup(html)
    #     for tag in soup.findAll(True):
    #         if tag.name not in allow_tags:
    #             s = ""
    #             for c in tag.contents:
    #                 if not isinstance(c, NavigableString):
    #                     c = cls.strip_tags(str(c), allow_tags)
    #                 s += str(c)
    #             tag.replaceWith(s)
    #     return soup
    #     pass

    @classmethod
    def node_to_string(cls, node):
        """`decode` is needed at the end because `etree.tostring`
        returns a python bytestring
        """
        return lxml.etree.tostring(node, method='html').decode()

    @classmethod
    def replace_tag(cls, node, tag):
        node.tag = tag

    @classmethod
    def strip_tags(cls, node, *tags):
        lxml.etree.strip_tags(node, *tags)

    @classmethod
    def get_element_by_id(cls, node, idd):
        selector = '//*[@id="%s"]' % idd
        elems = node.xpath(selector)
        if elems:
            return elems[0]
        return None

    @classmethod
    def get_elements_by_tag(
            cls, node, tag=None, attr=None, value=None, childs=False, use_regex=False) -> list:
        NS = None
        # selector = tag or '*'
        selector = 'descendant-or-self::%s' % (tag or '*')
        if attr and value:
            if use_regex:
                NS = {"re": "http://exslt.org/regular-expressions"}
                selector = '%s[re:test(@%s, "%s", "i")]' % (selector, attr, value)
            else:
                trans = 'translate(@%s, "%s", "%s")' % (attr, string.ascii_uppercase, string.ascii_lowercase)
                selector = '%s[contains(%s, "%s")]' % (selector, trans, value.lower())
        elems = node.xpath(selector, namespaces=NS)
        # remove the root node
        # if we have a selection tag
        if node in elems and (tag or childs):
            elems.remove(node)
        return elems

    @classmethod
    def append_child(cls, node, child):
        node.append(child)

    @classmethod
    def child_nodes(cls, node):
        return list(node)

    @classmethod
    def child_nodes_with_text(cls, node):
        root = node
        # create the first text node
        # if we have some text in the node
        if root.text:
            t = lxml.html.HtmlElement()
            t.text = root.text
            t.tag = 'text'
            root.text = None
            root.insert(0, t)
        # loop childs
        for c, n in enumerate(list(root)):
            idx = root.index(n)
            # don't process texts nodes
            if n.tag == 'text':
                continue
            # create a text node for tail
            if n.tail:
                # a string containing only newlines, tabs and spaces is useless
                text = n.tail if n.tail.split() else None
                t = cls.create_element(tag='text', text=text, tail=None)
                root.insert(idx + 1, t)
        return list(root)

    @classmethod
    def text_to_para(cls, text):
        return cls.from_string(text)

    @classmethod
    def get_children(cls, node):
        return node.getchildren()

    @classmethod
    def get_elements_by_tags(cls, node, tags):
        selector = 'descendant::*[%s]' % (
            ' or '.join('self::%s' % tag for tag in tags))
        elems = node.xpath(selector)
        return elems

    @classmethod
    def create_element(cls, tag='p', text=None, tail=None):
        t = lxml.html.HtmlElement()
        t.tag = tag
        t.text = text
        t.tail = tail
        return t

    @classmethod
    def get_comments(cls, node):
        return node.xpath('//comment()')

    @classmethod
    def get_parent(cls, node):
        return node.getparent()

    @classmethod
    def remove(cls, node):
        parent = node.getparent()
        if parent is not None:
            if node.tail:
                prev = node.getprevious()
                if prev is None:
                    if not parent.text:
                        parent.text = ''
                    parent.text += ' ' + node.tail
                else:
                    if not prev.tail:
                        prev.tail = ''
                    prev.tail += ' ' + node.tail
            node.clear()
            parent.remove(node)

    @classmethod
    def get_tag(cls, node):
        return node.tag

    @classmethod
    def get_text(cls, node):
        txts = [i for i in node.itertext()]
        return innerTrim(' '.join(txts).strip())

    @classmethod
    def previous_siblings(cls, node):
        """
            returns preceding siblings in reverse order (nearest sibling is first)
        """
        return [n for n in node.itersiblings(preceding=True)]

    @classmethod
    def previous_sibling(cls, node):
        return node.getprevious()

    @classmethod
    def next_sibling(cls, node):
        return node.getnext()

    @classmethod
    def is_text_node(cls, node):
        return True if node.tag == 'text' else False

    @classmethod
    def get_attribute(cls, node, attr=None):
        if attr:
            attr = node.attrib.get(attr, None)
            if attr:
                attr = unescape(attr)
        return attr

    @classmethod
    def delete_attribute(cls, node, attr=None):
        if attr:
            _attr = node.attrib.get(attr, None)
            if _attr:
                del node.attrib[attr]

    @classmethod
    def set_attribute(cls, node, attr=None, value=None):
        if attr and value:
            node.set(attr, value)

    @classmethod
    def outer_html(cls, node):
        e0 = node
        if e0.tail:
            e0 = deepcopy(e0)
            e0.tail = None
        return cls.node_to_string(e0)
