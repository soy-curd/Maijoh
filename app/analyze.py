#!/usr/bin/env python
# -*- coding: utf-8 -*-

from constants import *
import numpy as np
from pymongo import MongoClient
from collections import Counter
import itertools
import os
import tensorflow as tf
import random
from datetime import datetime
import sys

if not os.path.exists(CHECKPOINTS_DIR):
    os.makedirs(CHECKPOINTS_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


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
    labels = [one_hot_vec(l) for l in _labels]

    # 単語カウント
    ctr = Counter(itertools.chain(*contents))

    # [('a', 1), ...] -> ['a', ...]
    dictionaries = [c[0] for c in ctr.most_common()]
    dictionaries_inv = {c: i for i, c in enumerate(dictionaries)}

    if novels[0]["vector"]:
        return [novel["vector"] for novel in novels], labels, dictionaries

    # 各テキスト毎の単語ベクトル
    # [[ 3, 51, 34, 9, ...], ...]
    data = [[dictionaries_inv[word] for word in content] for content in contents]
    cursor = c.find()
    for novel, content in zip(cursor, contents):
        _id = novel["_id"]
        vector = [dictionaries_inv[word] for word in content]
        c.update({'_id': _id}, {'$set': {'vector': vector}})
    print(data, labels, dictionaries)
    return data, labels, dictionaries


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
    data = random.shuffle(zip(x, y))
    train_data = data[:NUM_TESTS]
    test_data = data[NUM_TESTS:]

    keep = tf.placeholder(tf.float32)

    """
    saver.restore(sess, "checkpoints/model-last")
    sess.run([predict_y], feed_dict={x_ph: random_test_x[0]})
    で行ける気がするが、型が合わない。謎。
    """


if __name__ == '__main__':
    main()
