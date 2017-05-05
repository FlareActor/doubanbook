import gensim

sentences = (['first', 'sentence'], ['second', 'sentence'])
model = gensim.models.Word2Vec(sentences, min_count=1)

# outp1 为输出模型
outp1 = 'wiki.zh.text.model'
# outp2为原始c版本word2vec的vector格式的模型
outp2 = 'wiki.zh.text.vector'

# model.save(outp1)
# model.wv.save_word2vec_format(outp2)
result = model.most_similar('first')
for each in result:
    print(each[0], each[1])
