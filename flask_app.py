import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_basicauth import BasicAuth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.rest import Client

# import json

# from flask_httpauth import HTTPBasicAuth
# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///December2021.db"
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'bapa'
app.secret_key = 'secret'

# APP VARIABLES
#using ints for time values
TIMESLOTS = [1000,1015,1030,1045,1100,1115,1130,1145,1200,1215,1230,1245,100,115,130,145,200,215,230,245]
MAXPEOPLEPERTIMESLOT = 40

basic_auth = BasicAuth(app)
db = SQLAlchemy(app)

class Person(db.Model):
	__tablename__ = 'registration'

	tmstmp = db.Column(db.Time)
	firstName = db.Column(db.String(128))
	lastName = db.Column(db.String(128))
	email = db.Column(db.String(128), primary_key=True)
	phone = db.Column(db.String(128))
	numAttending = db.Column(db.Integer)
	timeslot = db.Column(db.Integer)

	

	def __init__(self, firstName, lastName, email, phone, numAttending, timeslot):
		self.firstName = firstName
		self.lastName = lastName
		self.email = email
		self.phone = phone 
		self.numAttending = numAttending
		self.timeslot = timeslot

	def __repr__(self):
		return '<Person has name {}, {}>'.format(self.firstName+" "+self.lastName, self.numAttending)

	def serialize(self):
		return {
		    'firstName': self.firstName,
		    'lastName': self.lastName,
		    'email': self.email,
		    'phone' : self.phone,
		    'numAttending': self.numAttending,
		    'timeslot' : self.timeslot,
		    
		}

@app.route('/', methods=["GET", "POST"])
def index():
	if request.method == 'POST':
		email = request.form['email']
		fn = request.form['firstName']
		ln = request.form['lastName']
		pn = request.form['phone']
		na = request.form['numAttending']
		ts = request.form['timeslot']
		print(fn, ln, email, pn, na, ts)

		# check if pk email exists
		# Currently just gives an error. no option to update entry
		exists = db.session.query(Person.email).filter_by(email=email).first() is not None
		if (exists):
			flash("Error: A person with this email was already registered")
		else:
			person = Person(firstName = fn,
					 lastName = ln, 
					 email = email, 
					 phone = pn, 
					 numAttending = int(na),
					 timeslot = int(ts))

			db.session.add(person)
			db.session.commit()
			return redirect(url_for('done'))


	familiesPerSlot = [db.session.query(Person).filter(Person.timeslot == i).all() for i in TIMESLOTS]
	peoplePerSlot = [sum(fam.numAttending for fam in slot) for slot in familiesPerSlot]
	spaceRemaining = [MAXPEOPLEPERTIMESLOT - people for people in peoplePerSlot]
	
	return render_template('index.html', spaceRemainingPerTS = spaceRemaining)

@app.route('/done', methods=["GET"])
def done():
	return render_template('done.html')


@app.route('/admin', methods=["GET"])
@basic_auth.required
def admin():
	people = Person.query.all()
	return render_template('admin.html', allPeople=people)

#RUN THIS TO UPDATE DB SCHEMA
if __name__ == '__main__':
	db.create_all()
	app.run()
