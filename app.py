from __future__ import absolute_import

from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import pickle
from flask import Flask, session, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import quandl
import csv
import json
import sys

###### Add your API key here ##########
quandl.ApiConfig.api_key = ""
quandl.ApiConfig.api_version = '2015-04-09'

app = Flask(__name__, instance_relative_config=True)
# load the configurations
app.config.from_object('config')
app.config.from_pyfile('config.py')
# create database object
db = SQLAlchemy(app)

from models import *

def predict(query):
	with open("keras_tokenizer.pickle", "rb") as f:
   		tokenizer = pickle.load(f)
   	model = load_model("merger.hdf5")
	sequences = tokenizer.texts_to_sequences([query])
	data = pad_sequences(sequences, maxlen=300)
	return model.predict(data).tolist()


@app.route('/', methods = ['GET', 'POST'])
def index():
	"""Display dashboard with stock details(if any)
	   Display buttons for adding, deleting stocks
	"""
	# get current share price from the api for shares in database
	if(request.method == "GET"):
		tickers = db.session.query(AddShare.ticker).all()
		current_rate = []
		stock_list = []
		for t in tickers:
			stock_list.append("NSE/{}".format(t[0]))
		try:
			data = quandl.get(stock_list, column_index=4, rows=1, returns="numpy")
			for d in data[-1]:
				current_rate.append(d)
			# delete the date item from list and keep the last prices of shares in respective order
			del current_rate[0]
		except:
			flash("Error while fetching stock price(s) :-|")
		return render_template('dashboard.html', shares = AddShare.query.all(), data = current_rate)
	else:
		predictions = predict(request.form['data'])
		# sys.stdout.write("%s " %(request.form['data']))
		thingy = ["Buy", "Hold", "Sell"]
		# return "0"
		return thingy[predictions[0].index(max(predictions[0]))]

@app.route('/add_share', methods = ['GET', 'POST'])
def add():
	if request.method == 'POST':
		try:
			share = AddShare(name = request.form['share_name'].upper(),
							 date = datetime.strptime(request.form['buy_date'],'%Y-%m-%d'),
							 ticker = request.form['ticker'].upper(),
							 rate = request.form['rate'],
							 quantity = request.form['quantity'])
			db.session.add(share)
			db.session.commit()
			db.session.close()
			flash("Share added successfully")
		except:
			db.session.rollback()
			db.session.close()
			flash("An error occured while adding share")
		return redirect(url_for('index'))
	return redirect(url_for('index'))

if __name__ == '__main__':
	db.create_all()
	app.run(port=3000)
