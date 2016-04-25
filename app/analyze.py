#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import os
import sys
from collections import Counter
from datetime import datetime

import numpy as np
import tensorflow as tf
from pymongo import MongoClient

from constants import *

if not os.path.exists(CHECKPOINTS_DIR):
    os.makedirs(CHECKPOINTS_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def one_hot_vec(index):
    v = np.zeros(NUM_CLASSES)
    v[index] = 1
    return v


def padding(contents, max_word_count, padder='<PAD/>'):
    padded_contents = []
    for i in range(len(contents)):
        content = contents[i]
        padded_contents.append(content + [padder] * (max_word_count - len(content)))

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

    if "vector" in novels[0]:
        return [novel["vector"] for novel in novels], labels, dictionaries

    # 各テキスト毎の単語ベクトル
    # [[ 3, 51, 34, 9, ...], ...]
    data = [[dictionaries_inv[word] for word in content] for content in contents]
    cursor = c.find()
    for novel, content in zip(cursor, contents):
        _id = novel["_id"]
        vector = [dictionaries_inv[word] for word in content]
        c.update({'_id': _id}, {'$set': {'vector': vector}})
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
    for _id, words in contents:
        sentences = []
        sentence = []
        for word in words:
            if word in stop_words:
                sentences.append(sentence)
                if len(sentence) > max_size:
                    max_size = len(sentence)
                sentence = []
            else:
                sentence.append(word)

        c.update({'_id': _id}, {'$set': {'sentence_vectors': sentences}})

    # 長さを揃えるために0埋めする
    contents = [(novel["_id"], novel["sentence_vectors"]) for novel in novels]

    padder = 0
    for _id, sentences in contents:
        _sentences = padding(sentences, max_size, padder)
        c.update({'_id': _id}, {'$set': {'sentence_vectors': _sentences}})


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
    # x, y, d = get_data()
    def x2_plus_b(x, b):
        _x = tf.constant(x)
        _b = tf.constant(b)
        result = tf.square(_x)
        result = tf.add(result, _b)
        return result

    with tf.Session() as sess:
        result = sess.run([x2_plus_b(2, 3)])
        print(result)

    p_x = tf.placeholder(tf.float32)
    p_b = tf.placeholder(tf.float32)
    p_x2_plus_b = tf.add(tf.square(p_x), p_b)

    with tf.Session() as sess:
        result = sess.run([p_x2_plus_b], feed_dict={p_x: [2], p_b: [3]})
        print(result)

    """
    saver.restore(sess, "checkpoints/model-last")
    sess.run([predict_y], feed_dict={x_ph: random_test_x[0]})
    で行ける気がするが、型が合わない。謎。
    """


if __name__ == '__main__':
    main()
