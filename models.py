from __future__ import absolute_import
from app import db
from datetime import datetime

class AddShare(db.Model):
	"""adds a stock to the database.
	Input:
		date, ticker, rate, quantity
	Returns:
		String specifying the result of operation
	"""
	id = db.Column('share_no', db.Integer, primary_key = True, autoincrement = True)
	name = db.Column(db.String(50), nullable = False)
	date = db.Column(db.DateTime, nullable = False, default = datetime.now().strftime("%Y-%m-%d"))
	ticker = db.Column(db.String(10), nullable = False)
	rate = db.Column(db.Float, nullable = False)
	quantity = db.Column(db.Integer, nullable = False)


