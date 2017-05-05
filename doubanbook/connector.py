"""
软件工程-医疗搜索项目
"""

from sklearn.feature_extraction.text import CountVectorizer, HashingVectorizer, TfidfVectorizer
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import Pipeline
from functools import reduce
import jieba as jb
import pymysql
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
import numpy as np
import gensim

"""连接数据库"""
db = pymysql.connect(host='localhost', port=3306, user='root', passwd='605160',
                     db='db_qiuyi', charset='utf8', autocommit=True)  # InnoDB
# db = pymysql.connect(host='172.20.45.88', port=3306, user='medicalteam', passwd='medicalteam_2017',
#                      db='db_qiuyi', charset='utf8', autocommit=True)
# print("数据库编码为：", db.__dict__['charset'])  # 默认为latin1
cur = db.cursor()

"""更新疾病的搜索指数"""
# import_data = pd.read_csv('data/index.csv')[["关键词", "整体指数"]]
# import_data = import_data[(import_data["整体指数"] != "--") & (import_data["整体指数"] != "0")]
# import_data.apply(axis=1, func=lambda row: cur.execute(
#     "UPDATE db_qiuyi.tb_ill SET search_index = %d WHERE name = '%s';" % (int(row[1]), row[0])))

"""导出疾病名称"""
# cur.execute("select name from db_qiuyi.tb_ill")
# df = pd.DataFrame({'name': cur.fetchall()})
# df['name'] = df['name'].map(lambda x: x[0])
# df.to_csv('data/illname.csv', index=False)

"""计算向量相似性"""


def flatten_tokens(tokens):
    flat_str = ""
    for token in tokens:
        if isinstance(token, list):
            for i in token:
                flat_str += i
                flat_str += ","
        else:
            flat_str += token
            flat_str += ","
    return flat_str.strip(",")


def cross_tokens(tokens, cross=True):
    tokens = list(split_tokens(tokens))
    return [token for token in tokens] + (
        [i + j for i in tokens for j in tokens if i != j and len(i) + len(j) < 4] if cross else [])


def split_tokens(tokens):
    ban_tokens = [","]
    tokens = tokens.replace("有点", "")
    return (token for token in jb.cut_for_search(tokens) if token not in ban_tokens)


def find_max_indexes(sparse_mat):
    max_values = csr_matrix(sparse_mat.max(axis=0) * 0.6)
    max_indexes = []
    for i in range(0, max_values.shape[1]):
        max_index = []
        if max_values[0, i] > 0:
            for j in range(0, sparse_mat.shape[0]):
                if max_values[0, i] <= sparse_mat[j, i]:
                    max_index.append(j + 1)
        max_indexes.append(max_index)
    return max_indexes


cur.execute("select symptom from db_qiuyi.tb_ill")
df = pd.DataFrame({'symptom': cur.fetchall()}).applymap(
    lambda row: flatten_tokens(cross_tokens(str(row[0]), False)))


class words(object):
    def __iter__(self):
        for i in df.symptom:
            yield str(i).split(",")


model = gensim.models.Word2Vec(sentences=words(), min_count=1)
result = model.most_similar(u'呼吸困难')
for each in result:
    print(each[0], each[1])

print(df)

list1 = [u'头', u'痛']
list2 = [u'小子']
list_sim1 = model.n_similarity(list1, list2)
print(list_sim1)

"""疾病向量化并投影到主题空间"""
# svd = TruncatedSVD(n_components=2000)
# pipe_washing = Pipeline([
#     ("vector", TfidfVectorizer(tokenizer=lambda x: x.split(","), binary=False))
#     # , ("normalizer", Normalizer())
#     , ("svd", svd)
# ])
# X_train = pipe_washing.fit_transform(df.symptom)
# print(X_train.shape)
# print(np.cumsum(svd.explained_variance_ratio_))

"""关闭连接"""
# cur.close()
# db.close()


if __name__ != "__main__":
    from time import time

    while True:
        tokens = input("Enter your input: ")
        t0 = time()
        X_test = [flatten_tokens(cross_tokens(tokens))]
        print("分词向量：", X_test, list(jb.cut_for_search(X_test[0])))
        X_test = pipe_washing.transform(X_test)
        result = X_train * np.mat(X_test).T
        # print("Answers:", find_max_indexes(result))
        print("Time:%ss" % str(time() - t0))
        result = find_max_indexes(result)[0]
        if len(result) > 0:
            cur.execute(
                "SELECT name,symptom FROM db_qiuyi.tb_ill WHERE id in (%s)" % str(result).strip("[]"))
            for i in cur.fetchall():
                print(i)
    pass
