# -*- encoding: utf-8 -*-
# (C) Copyright 2008 Tarek Ziadé <tarek@ziade.org>
#
import os

from atomisator.enhancers import DiggComments
from atomisator.enhancers import RelatedEntries
from atomisator.enhancers import PostRanked
from atomisator.enhancers.digg import Digg

from nose.tools import *

def setup():
    class Story:
        id = u'9878756'

    def one(*args, **kw):
        return [Story()]
    
    global old, old2
    old = Digg.getStories
    Digg.getStories = one

    class Comment:
        content = 'good comment'

    def one_comment(*args, **kw):
        return [Comment()]
    
    old2 = Digg.getStoriesComments
    Digg.getStoriesComments = one_comment

def teardown():
    Digg.getStories = old
    Digg.getStoriesComments = old2

@with_setup(setup, teardown)
def test_digg():

    class E:
        link = 'http://mail.python.org/pipermail/python-dev/2006-December/070323.html'
        title = summary = 'xxx'
    entry =  E()
    d = DiggComments()
    entry = d(entry, [])
    assert '<li>' in entry.summary

def test_related():
   
    class E:
        title = id = u'1'
        summary = 'my summary'
        tags = ['one', 'two']
        links = ['http://link/one']
        link = 'http://example.com/one'

    class E2:
        title = id = u'2'
        summary = 'other summary'
        tags = ['two', 'three']
        link = 'http://example.com/two'
        links = []
    
    r = RelatedEntries()
    entry = E()
    entries = [E(), E2()]
    r.prepare(entries)
    
    wanted = ['one', 'three', 'two']
    have = r._tags.keys()
    have.sort()
    assert_equals(wanted, have)
    assert_equals([e.id for e in r._tags['two']], [u'1', u'2'])
    assert_equals([e.id for e in r._tags['three']], [u'2'])
    assert_equals([e.id for e in r._tags['one']], [u'1'])

    entry = r(entry)
 
    # common tags   
    assert 'http://example.com/two' in entry.summary

def test_related_link():

    dirname = os.path.dirname(__file__)
    sample1 = os.path.join(dirname, 'sample1.html')
    sample2 = os.path.join(dirname, 'sample2.html')

    class E:
        title = id = u'1'
        summary = open(sample1).read().decode('utf8') 
        tags = []
        links = []
        link = 'http://example.com/one'

    class E2:
        title = id = u'2'
        summary = open(sample2).read().decode('utf8')
        tags = ['two', 'three']
        link = 'http://example.com/two'
        links = []

    r = RelatedEntries()
   
    e1, e2 = E(), E2()
    entry = e1
    entries = [e1, e2]       
    r.prepare(entries) 
    links = r._get_content_link(E.summary)
    assert u'http://www.python.org' in links
    assert_equals(len(links), 21)

    assert_equals(r._links[u'http://www.python.org'], [e1, e2])
    entry = r(entry)
    assert '<strong>Related</strong>' in entry.summary

def test_post_rank():

    postrank_res = [('{ "http:\\/\\/tarekziade.wordpress.com\\/2008'
                     '\\/11\\/27\\/expert-python-programming-book-typo'
                     '-sprint-tonight\\/": { "postrank": 5.3,' 
                     '"postrank_color": "#ffaf61" } }'), 
                     {('http://tarekziade.wordpress.com/2008/11/27/'
                       'expert-python-programming-book-typo-sprint-tonight/'):
                     {'postrank_color': '#ffaf61', 'postrank': 5.3}}]

    postrank_id = ['dontcare', {'feed_id': 87554}]
    class E2:
        title = id = 'Expert Python Programming Book : typo sprint tonight'
        summary = ''
        link = ('http://tarekziade.wordpress.com/2008/11/27/'
                'expert-python-programming-book-typo-sprint-tonight/')
        root_link = 'http://tarekziade.wordpress.com/feed/atom'

    ranker = PostRanked()

    # faking postrank webservice
    class FakePR(object):
        def __call__(self, *args, **kw):
            if args[0] == 'feed_id':
                return postrank_id
            return postrank_res

    ranker._post_rank = FakePR()
    result = ranker(E2())
    assert_equals(result.summary, 
                  '<div class="postrank">PostRank: 5.3</div>\n')

    
    # now we filter out any postrank < 7.0
    res = ranker(E2(), treshold='7.0')
    assert res is None

