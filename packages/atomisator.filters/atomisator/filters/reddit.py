# -*- encoding: utf-8 -*-
# (C) Copyright 2008 Tarek Ziadé <tarek@ziade.org>
#
from sgmllib import SGMLParser
import re
import urllib2
import string

from BeautifulSoup import BeautifulSoup, Comment

options = re.DOTALL | re.UNICODE | re.MULTILINE | re.IGNORECASE
TAGS = ('p', 'i', 'strong', 'b', 'u', 'a', 'h1', 'h2', 'h3', 'br', 'img')
ATTRS = ('href', 'src', 'title')

class Html2Txt(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.pieces = []

    def handle_data(self, text):
        self.pieces.append(text)

    def handle_entityref(self, ref):
        if ref == 'amp':
            self.pieces.append("&")

    def output(self):
        return ' '.join(self.pieces)

class RedditFollower(object):
    """
    Will detect a reddit-like post and fill the summary
    of the entry with an extract of the target page 
    by following the link.

    The filter tries to pick up the best extract out
    of the page.
    """
    pattern = r'<a href="(.*)">\[link\]</a> <a href=".*?">\[comments\]</a>'

    def __call__(self, entry, entries):
        summary = entry.get('summary', '')
        link = re.search(self.pattern, summary, options) 
        if link is None:
            return entry

        # reddit-like detected
        link = link.groups()[0]

        # let's get a sample of the link
        sample, encoding = self._get_sample(entry['title'], link)
        if sample is not None:
            extract = '<div>Extract from link :</div> <p>%s</p><br/>' % \
                    sample.decode(encoding)            
            entry['summary'] = extract + entry['summary']
        return entry
 
    def _clean(self, value):
        """cleans an html page."""
        soup = BeautifulSoup(value)

        # removes unwanted tags (security+style)
        for comment in soup.findAll(
            text = lambda text: isinstance(text, Comment)):
            comment.extract()
        for tag in soup.findAll(True):
            if tag.name not in TAGS:
                tag.hidden = True
            tag.attrs = [(attr, val) for attr, val in tag.attrs
                        if attr in ATTRS]

        # loads and render 
        parser = Html2Txt()
        parser.reset()
        parser.feed(soup.body.renderContents())
        parser.close()
        return parser.output().strip()

    def _words(self, data):
        data = ''.join([w for w in data if w in string.ascii_letters+' '])
        return [w.strip() for w in data.split()]

    def _combos(self, lists):
        if len(lists) == 1: 
            return [(x,) for x in lists[0]]
        return [(i,) + j for j in self._combos(lists[1:]) for i in lists[0]]

    def _extract(self, title, content, size):
        """will try to find the best extract"""
        delta = size / 2.
        lcontent = content.lower()

        # finding the positions for all the words
        def _indexes(word, content):
            return [e.start() for e in re.finditer(word.strip(), 
                                                   content, options)]
        
        # voir pour extraire un pattern
        positions = [_indexes(w, lcontent) for w in self._words(title) 
                     if _indexes(w, lcontent) != []]
                
        # creating all the combos, and calculating the
        # amplitude for each
        series = [(self._ampl(combo), combo) 
                  for combo in self._combos(positions)]

        # sorting, then we have the part of the text
        # with the maximum occurences of words
        series.sort()
        seq = series[0][1]
        start, end = min(seq), max(seq)
        if end - start > size:
            end = start + size
            
        return '...' + content[start:end] + '...'
 
    def _ampl(self, seq):
        return max(seq) - min(seq)

    def _get_sample(self, title, link, size=300):
        """get the page, extract part of it if it is some text.
        
        tries to find the words of the title, to extract 
        the most meaningful part of the page.
        """
        charset = 'utf-8'
        try:
            page = urllib2.urlopen(link)
            if 'content-type' in page.headers.keys():
                content_type = page.headers['content-type'].split(';')
                type_ = content_type[0].strip().lower()
                if type_ not in ('text/html', 'text/plain', 'test/rst'):
                    return None, None
                if len(content_type) > 1:
                    charset = content_type[1].split('=')[-1]
            content = page.read()

        except urllib2.HTTPError:
            return None, None

        body = self._clean(content)
        return self._extract(title, body, size), charset
