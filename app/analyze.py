#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import os
import sys
from collections import Counter
from datetime import datetime

import numpy as np
from pymongo import MongoClient

from constants import *

if not os.path.exists(CHECKPOINTS_DIR):
    os.makedirs(CHECKPOINTS_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def one_hot_vec(index):
    v = np.zeros(NUM_CLASSES)
    if index > NUM_CLASSES:
        return []
    v[index] = 1
    return v


def padding(contents, max_word_count, padder='<PAD/>'):
    padded_contents = []
    for i in range(len(contents)):
        content = contents[i]
        padded_contents.append(content + [padder] * (max_word_count - len(content)))

    return padded_contents


def make_data(with_sentence=True):
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
    labels = [one_hot_vec(l) for l in _labels]

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

    if with_sentence:
        data, labels = make_sentence_vector()

    return data, labels, dictionaries


def make_sentence_vector():
    stop_words = [3]  # "。"

    # MongoDB接続
    mongo_client = MongoClient('localhost:27017')
    # データベース選択
    db_connect = mongo_client["novel"]
    c = db_connect.novel
    cursor = c.find()
    novels = [novel for novel in cursor]
    contents = [(novel["_id"], novel["vector"]) for novel in novels]

    # "。"で区切る
    max_size = 0
    max_word = 0
    for _id, words in contents:
        sentences = []
        sentence = []
        for word in words:
            if word > max_word:
                max_word = word
            if word in stop_words:
                sentences.append(sentence)
                if len(sentence) > max_size:
                    max_size = len(sentence)
                sentence = []
            else:
                sentence.append(word)

        c.update({'_id': _id}, {'$set': {'sentence_vectors': sentences}})

    # 長さを揃えるために0埋めする
    contents = [(novel["_id"], novel["sentence_vectors"], novel["label"]) for novel in novels]

    padder = 0
    data = []
    labels = []
    for _id, sentences, label in contents:
        _sentences = padding(sentences, max_size, padder)
        c.update({'_id': _id}, {'$set': {'sentence_vectors': _sentences}})
        if label != 100:  # 舞城のデータは訓練に用いない
            data = data + _sentences
            _label = one_hot_vec(label)
            labels = labels + [_label for _ in range(len(_sentences))]

    return data, labels


def get_data():
    if os.path.exists(DATA_FILE) and os.path.exists(LABEL_FILE) and os.path.exists(DICTIONARY_FILE):
        data = np.load(DATA_FILE)
        labels = np.load(LABEL_FILE)
        dictionaries = np.load(DICTIONARY_FILE)
    else:
        data, labels, dictionaries = make_data()
        data = np.array(data)
        labels = np.array(labels)
        dictionaries = np.array(dictionaries)

        np.save(DATA_FILE, data)
        np.save(LABEL_FILE, labels)
        np.save(DICTIONARY_FILE, dictionaries)

    return data, labels, dictionaries


def log(content):
    time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(time + ': ' + content)
    sys.stdout.flush()


def main():
    x, y, d = get_data()


if __name__ == '__main__':
    main()
