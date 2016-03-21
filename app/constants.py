#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Author(object):
    def __init__(self, name, aozora_num):
        self.name = name
        self.aozora_num = aozora_num
        self.class_num = None


AUTHORS = [
    Author("坂口安吾", 1095),
    Author("江戸川乱歩", 1779),
    Author("折口信夫", 933),
    Author("夢野久作", 96)
]
for i, author in enumerate(AUTHORS):
    author.class_num = i

AUTHOR_CLASS = {author.name: author.class_num for author in AUTHORS}

NUM_TESTS = 20
NUM_CLASSES = len(AUTHORS)
NUM_EPOCHS = 10
NUM_MINI_BATCH = 64
EMBEDDING_SIZE = 128
NUM_FILTERS = 128
FILTER_SIZES = [3, 4, 5]
L2_LAMBDA = 0.0001
EVALUATE_EVERY = 100
CHECKPOINTS_EVERY = 1000

SUMMARY_LOG_DIR = 'summary_log'
CHECKPOINTS_DIR = 'checkpoints'

DATA_DIR = 'data'
RAW_FILE = 'data/raw.txt'
DATA_FILE = 'data/data.npy'
LABEL_FILE = 'data/labels.npy'
DICTIONARY_FILE = 'data/dictionaries.npy'
