import os, nltk, telebot

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
nltk.download("wordnet")
import numpy as np, json

from keras.layers import Dense, SimpleRNN, Input, Embedding, LSTM
from keras.models import Sequential
from keras_preprocessing.text import Tokenizer, text_to_word_sequence
from keras.utils import to_categorical

with open('text', 'r', encoding='utf-8') as f:
  texts = f.read()
  texts = texts.replace('\ufeff', '')  # убираем первый невидимый символ

lemmatize = nltk.WordNetLemmatizer()

maxWordsCount = 1000
tokenizer = Tokenizer(num_words=maxWordsCount,
                      filters='!–"—#$%&amp;()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r«»',
                      split=' ',
                      char_level=False)
tokenizer.fit_on_texts([texts])

dist = list(tokenizer.word_counts.items())
print(dist[:10])

data = tokenizer.texts_to_sequences([texts])
# res = to_categorical(data[0], num_classes=maxWordsCount)
# print(res.shape)
res = np.array(data[0])

inp_words = 3
n = res.shape[0] - inp_words

X = np.array([res[i:i + inp_words] for i in range(n)])
Y = to_categorical(res[inp_words:], num_classes=maxWordsCount)

model = Sequential()
model.add(Embedding(maxWordsCount, 256, input_length=inp_words))
model.add(SimpleRNN(128, activation='tanh', return_sequences=True))
model.add(SimpleRNN(128, activation='relu', return_sequences=True))
model.add(SimpleRNN(128, activation='softplus', return_sequences=True))
model.add(SimpleRNN(128, activation='sigmoid'))
model.add(Dense(maxWordsCount, activation='softmax'))
model.summary()
model.compile(loss='categorical_crossentropy',
              metrics=['accuracy'],
              optimizer='adam')

history = model.fit(X, Y, batch_size=32, epochs=130)


def buildPhrase(texts, str_len=20):
  res = texts
  data = tokenizer.texts_to_sequences([texts])[0]
  for i in range(str_len):
    # x = to_categorical(data[i: i + inp_words], num_classes=maxWordsCount)  # преобразуем в One-Hot-encoding
    # inp = x.reshape(1, inp_words, maxWordsCount)
    x = data[i:i + inp_words]
    inp = np.expand_dims(x, axis=0)

    pred = model.predict(inp)
    indx = pred.argmax(axis=1)[0]
    data.append(indx)

    res += " " + tokenizer.index_word[indx]  # дописываем строку

  return res
