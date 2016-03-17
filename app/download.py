#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import urllib.request
from urllib.parse import quote

import igo
from bs4 import BeautifulSoup
from pymongo import MongoClient


class Novel(object):
    def __init__(self, title, author, body, url, children=[], wakati_text=None):
        self.title = title
        self.author = author
        self.body = body
        self.url = url
        self.children = children
        self.wakati_text = wakati_text


class NovelSite(object):
    def download_html(self, source_url):
        res = urllib.request.urlopen(source_url)
        return res.read()

    def get_body_text(self, text, url=None):
        raise NotImplementedError()


class Kakuyomu(NovelSite):
    def __init__(self):
        self.domain = "https://kakuyomu.jp"
        self.search_url = self.domain + "/search?q={0}"

    def download_html(self, source_url):
        res = urllib.request.urlopen(source_url)
        return str(res.read(), 'utf-8')

    def get_novel_link(self, search_key="SF"):
        html = self.download_html(self.search_url.format(quote(search_key)))
        soup = BeautifulSoup(html)
        articles = soup.find_all('div', {'class': 'widget-work float-parent'})
        results = []
        for article in articles:
            title_obj = article.find('a', {'class': 'widget-work-titleLabel'})
            title = title_obj.string
            url = self.domain + title_obj['href']
            author = article.find('a', {'class': 'widget-work-authorLabel'}).string
            children = self.get_episodes(url)
            n = Novel(title, author, "", url, children)
            results.append(n)

        return results

    def get_episodes(self, url):
        html = self.download_html(url)
        soup = BeautifulSoup(html)
        episodes = soup.find_all('li', {'class': 'widget-toc-episode'})
        results = []
        for episode in episodes:
            _url = self.domain + episode.find('a')['href']
            _html = self.download_html(_url)
            novel = self.get_body_text(_html, _url)
            results.append(vars(novel))
        return results

    def get_body_text(self, text, url=None):
        soup = BeautifulSoup(text)
        try:
            title = soup.find('p', {'class': 'widget-episodeTitle'}).text
        except AttributeError:
            title = ""
        try:
            author = soup.find('p', {'id': 'contentMain-header-author'}).text
        except AttributeError:
            author = ""
        try:
            body = soup.find('div', {'class': 'widget-episodeBody'}).text
        except AttributeError:
            body = ""
        body = re.sub('<.+?>', "", body)

        novel = Novel(title, author, body, url)
        return novel


def wakati(text):
    t = igo.Tagger.Tagger('ipadic')

    return t.wakati(text)


def main():
    # MongoDB接続
    mongo_client = MongoClient('localhost:27017')
    # データベース選択
    db_connect = mongo_client["novel"]

    # kakuyomu = Kakuyomu()
    # novels = kakuyomu.get_novel_link("人外")
    #
    # # データ挿入
    # for novel in novels:
    #     db_connect["novel"].insert_one(vars(novel))

    c = db_connect.novel
    cursor = c.find()
    for novel in cursor:
        _id = novel["_id"]
        new_children = []
        for episode in novel["children"]:
            episode["wakati_text"] = wakati(re.sub("\n", "", episode["body"]))
            new_children.append(episode)

        c.update({'_id': _id}, {'$set': {'children': new_children}})


if __name__ == '__main__':
    main()
