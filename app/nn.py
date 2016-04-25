import math

# 入力層: ノード数9
# 入力A
A = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 入力B
B = [1, 2, 3, 4, 5, 6, 10, 8, 9]

A_OUT = 1
B_OUT = 0


def sigmoid(x):
    # シグモイド関数を定義
    # 0から1までの間の連続値を得られる
    return 1.0 / (1.0 + math.exp(-x))


# 隠れ層: ノード数3
def hoge(inputs):
    weights = [0.1, -0.2, 0.3]  # 適当な値
    ret = []
    for w in weights:
        # それぞれの重みをかけた値を加算
        h = sum([input * w for input in inputs])
        ret.append(sigmoid(h))

    return ret


# 出力層: ノード数2
def fuga(hiddens):
    weights = [-0.1]  # 適当な値
    ret = []
    for w in weights:
        # それぞれの重みをかけた値を加算
        o = sum([hidden * w for hidden in hiddens])
        ret.append(sigmoid(o))

    return ret


y1 = fuga(hoge(A))  # -> これをA_OUTに近づけたい
y2 = fuga(hoge(B))  # -> これをB_OUTに近づけたい
print(y1, y2)