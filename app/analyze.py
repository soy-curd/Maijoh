#!/usr/bin/env python
# -*- coding: utf-8 -*-

from download import Novel
from constants import *
import numpy as np
from pymongo import MongoClient
from collections import Counter
import itertools


def one_hot_vec(index):
    v = np.zeros(NUM_CLASSES)
    v[index] = 1
    return v


def padding(contents, max_word_count):
    padded_contents = []
    for i in range(len(contents)):
        content = contents[i]
        padded_contents.append(content + ['<PAD/>'] * (max_word_count - len(content)))

    return padded_contents


def make_data():
    # MongoDB接続
    mongo_client = MongoClient('localhost:27017')
    # データベース選択
    db_connect = mongo_client["novel"]
    c = db_connect.novel
    cursor = c.find()
    novels = [novel for novel in cursor]
    contents = [novel["wakati_text"] for novel in novels]

    contents = padding(contents, max([len(c) for c in contents]))
    _labels = [novel["label"] for novel in novels]
    print(_labels)
    labels = [one_hot_vec(l) for l in _labels]
    if novels[0]["vector"]:
        return labels, [novel["vector"] for novel in novels]

    # 単語カウント
    ctr = Counter(itertools.chain(*contents))

    # [('a', 1), ...] -> ['a', ...]
    dictionaries = [c[0] for c in ctr.most_common()]
    dictionaries_inv = {c: i for i, c in enumerate(dictionaries)}

    # 各テキスト毎の単語ベクトル
    # [[ 3, 51, 34, 9, ...], ...]
    data = [[dictionaries_inv[word] for word in content] for content in contents]
    cursor = c.find()
    for novel, content in zip(cursor, contents):
        _id = novel["_id"]
        vector = [dictionaries_inv[word] for word in content]
        c.update({'_id': _id}, {'$set': {'vector': vector}})

    return labels, data


def main():
    labels, data = make_data()
    print(labels)


if __name__ == '__main__':
    main()
