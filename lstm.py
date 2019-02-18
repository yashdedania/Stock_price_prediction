import json
from keras.layers import Embedding, LSTM, Dense, Conv1D, MaxPooling1D, Dropout, Activation
from keras.models import Sequential
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences	
import pickle
import quandl
from datetime import datetime
from datetime import timedelta
import numpy as np
from numpy import genfromtxt
from keras.utils import to_categorical
import pickle
import os
import glob
       
# Tip: col 3 is open in quandl coulmn-index

# generate labels
labels = []
articles = {}
train_data = []

quandl.ApiConfig.api_key = "4gz5dBz2-gfA1wJtfswe"
quandl.ApiConfig.api_version = '2015-04-09'


# helper method to prepare training data and labels
def parse_data(file_name, stock_name):
    with open(file_name, 'r') as f:
        c = json.load(f)
    print("Loading " + stock_name + " " +file_name)
    train_data.append(c['text'].encode('utf-8'))
    e_date = datetime.strptime(c["time"].split(" ")[0], '%Y-%m-%d') + timedelta(days=5)
    data = quandl.get("NSE/{}".format(stock_name), column_index=5, start_date = c["time"].split(" ")[0], end_date = e_date, returns="numpy")

    diff = ((data[-1][1] - data[0][1])/data[0][1])*100 
    if(diff > 1.5):
        label = 0
    elif(diff < 1.5 and diff > -1.5):
        label = 1
    else:
        label = 2
    print(label)
    labels.append(label)

stocks = ['ONGC','RELIANCE', 'BHEL']
for stock in stocks:
    # create path
    for fn in glob.glob(os.path.join('Oil&Gas', stock, '*')):
        parse_data(fn, stock)


# save labels and train data

labels = to_categorical(labels) 

with open('articles.txt', 'w') as outfile:  
    json.dump(train_data, outfile)

np.savetxt("labels.csv", labels, delimiter=",")

# with open('articles.txt', 'r') as f:
#         articles = json.load(f)

# labels = genfromtxt('labels.csv', delimiter=',')


tokenizer = Tokenizer(num_words=20000, filters='!"#&()*,./:;?@[\\]^_`{|}~\t\n')
toytexts = ["Is is a common word", "So is the", "the is common", "discombobulation is not common"]
tokenizer.fit_on_texts(train_data)
sequences = tokenizer.texts_to_sequences(train_data)

# print(tokenizer.word_index)

padded_sequences = pad_sequences(sequences, maxlen=300)

# print(padded_sequences)

model = Sequential()
model.add(Embedding(20000, 128, input_length=300))
model.add(Dropout(0.2))
model.add(Conv1D(64, 5, activation='relu'))
model.add(MaxPooling1D(pool_size=4))
model.add(LSTM(128))
model.add(Dense(3, activation='sigmoid'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(padded_sequences, np.array(labels), validation_split=0.2, epochs=10)

# save the tokenizer and model
with open("keras_tokenizer.pickle", "wb") as f:
   pickle.dump(tokenizer, f)
model.save("new_merger.hdf5")



