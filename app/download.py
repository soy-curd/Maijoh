#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import time
import urllib.request
from urllib.parse import quote, urljoin

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

    def get_novel(self, search_key="SF"):
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


class Aozora(NovelSite):
    def __init__(self):
        self.domain = 'http://www.aozora.gr.jp'

    def download_html(self, source_url):
        res = urllib.request.urlopen(source_url)
        return str(res.read(), 'shift-jis')

    def get_novel(self, author_num=35):
        url = 'http://www.aozora.gr.jp/index_pages/person{}.html'.format(author_num)
        return self.download_novel(url)

    def download_novel(self, url, max_cnt=10):
        hostname = 'http://www.aozora.gr.jp'

        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html)

        all_al = soup.find_all('ol')
        novel_links = all_al[0]

        novels = []
        cnt = 0
        for x in novel_links.find_all('li'):
            link = x.a['href']
            title = x.text
            novels.append(Novel(title, author="", body="", url=link))
            cnt += 1
            if cnt == max_cnt:
                break

        for novel in novels:
            url = hostname + novel.url[2:]
            html = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(html)

            download_table = soup.find('table', {'class': 'download'})
            units = download_table.find_all('tr', {'bgcolor': 'white'})
            for unit in units:
                link = unit.find('a')['href']
                _, ext = os.path.splitext(link)
                print(unit, link, _, ext)
                if ext == '.html':
                    novel.url = urljoin(url, link)
                    break

            # クローリングのため一応スリープ
            time.sleep(0.5)

        for novel in novels:
            try:
                body = self.download_html(novel.url)
                body, title, author = self.remove_ruby(body)
                novel.body = body
                novel.title = title
                novel.author = author
            except:
                print(novel.url)

        return novels

    def remove_ruby(self, text):
        soup = BeautifulSoup(text)
        title = soup.find('h1', {'class': 'title'}).text
        author = soup.find('h2', {'class': 'author'}).text
        tag = soup.div

        # ここでルビをreplaceする必要がある。
        try:
            while soup.ruby:
                tag.ruby.replace_with(tag.ruby.rb.string)
            while soup.br:
                soup.br.decompose()
            while soup.strong:
                soup.strong.decompose()
        except AttributeError:
            pass

        _text = tag.text

        return _text, title, author


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

    aozora = Aozora()
    # 安吾、乱歩、信夫、久作
    authores = [1095, 1779, 933, 96]
    novels = []
    for author in authores:
        novels += aozora.get_novel(author)

    # データ挿入
    for novel in novels:
        db_connect["novel"].insert_one(vars(novel))

    c = db_connect.novel
    cursor = c.find()
    for novel in cursor:
        _id = novel["_id"]
        new_children = []
        if novel["children"]:
            for episode in novel["children"]:
                episode["wakati_text"] = wakati(re.sub("\n", "", episode["body"]))
                new_children.append(episode)

            c.update({'_id': _id}, {'$set': {'children': new_children}})
        else:
            wakati_text = wakati(re.sub("\n", "", novel["body"]))
            c.update({'_id': _id}, {'$set': {'wakati_text': wakati_text}})


if __name__ == '__main__':
    main()
