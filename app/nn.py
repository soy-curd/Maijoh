import math

# 入力層: ノード数9
# 入力A
A = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 入力B
B = [1, 2, 3, 4, 5, 6, 10, 8, 9]

A_OUT = [1, 0]
B_OUT = [0, 1]


def softmax(xs):
    # ソフトマックス関数を定義
    # 0から1までの間の連続値を得られる
    e = [math.exp(x) for x in xs]
    sum_e = sum(e)
    return [x / sum_e for x in xs]


def hoge(inputs):
    weights = [0.1, -0.2]  # 適当な値
    bias = 0.001  # 適当な値
    ret = []
    for w in weights:
        # それぞれの重みをかけた値を加算
        h = sum([input * w for input in inputs]) + bias
        ret.append(h)

    return softmax(ret)


y1 = hoge(A)  # -> これをA_OUTに近づけたい!
y2 = hoge(B)  # -> これをB_OUTに近づけたい!
print(y1, y2)