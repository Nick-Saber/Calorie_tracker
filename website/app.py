from flask import Flask, render_template, url_for, request, redirect, session
import psycopg2 as psql
from psycopg2.extensions import AsIs, QuotedString
import json
import db_api


# from flask.ext.sqlalchemy import SQLAlchemy
import os
secret_key = os.urandom(24)

app = Flask(__name__)


@app.route('/',  methods= ['GET','POST'])
def login():
	dict_variables={}

	#Process Logging In
	if request.method=='POST':
		#If routed here from logging out
		if request.form.get('login_type')=='Logout':
			session['username']=None
			dict_variables['user']=session['username']
			return render_template('login.html',dict_variables=dict_variables)
		#Account creation
		if request.form.get('login_type')=='Create':
			if (request.form.get('password1')==request.form.get('password2')) and (request.form.get('user_name')!= None):
				if db_api.add_user(request.form.get('user_name'),request.form.get('password1')):
					session['username']=request.form.get('user_name')
					dict_variables['user']=session.get('username')
					return render_template('entry_page.html',dict_variables=dict_variables)
				else:
					dict_variables['create_acc_error_message']='Error with account creation, Invalid Credentials'
					return render_template('login.html',dict_variables=dict_variables)
			else:
				dict_variables['create_acc_error_message']='Error with account creation, Passwords don\'t match'
				return render_template('login.html',dict_variables=dict_variables)

		#Logging in to an existing account
		if request.form.get('login_type')=='Login':
			#result is a tuple where the boolean value of the check is the first entry and
			#the second entry is the associated error or success message
			result= db_api.check_login(request.form.get('user_name_login'),request.form.get('login_password'))
			if result[0]:
				session['username']=request.form.get('user_name_login')
				dict_variables['user']=session['username']
				return render_template('entry_page.html',dict_variables=dict_variables)
			else:
				dict_variables['login_acc_error_message']=result[1]
				return render_template('login.html',dict_variables=dict_variables)


	if request.method=='GET':		
		dict_variables['user']=session.get('username')
		return render_template('login.html' , dict_variables=dict_variables)



@app.route('/entry_page', methods=['GET','POST'] )
def entry_page():
	dict_variables={}
	#always plot and display the users past 5 entries
	if session.get('username') != None:
		#plot users past history data
		history_data=db_api.get_past_x_days(session.get('username'),5)
		dict_variables['caloric_history_values']=json.dumps(history_data[0])
		dict_variables['caloric_history_dates']=json.dumps([entry.__str__() for entry in history_data[1]])
		dict_variables['history_length'] = len(history_data[0])

	if request.method == 'GET':
		if request.args.get('user_name') != None :
			session['username']=request.args.get('user_name')
			dict_variables['user']=session.get('username')

			return  render_template('entry_page.html',dict_variables=dict_variables)
		elif session.get('username') != None:
			dict_variables['user']=session.get('username')
			return  render_template('entry_page.html',dict_variables=dict_variables)
		else:
			return redirect(url_for('login'))

	if request.method =='POST':
		if (request.form.get('food_item') != '') and (request.form.get('caloric_value') !=''):
			# add_food_entry(request.form['food_item'] ,request.form['caloric_value'],session['username'])
			#store user information to pass into template
			dict_variables['user']=session.get('username')
			dict_variables['display_message']=True
			dict_variables['message']="last entry was food: " +request.form['food_item'] +"  calories: " + request.form['caloric_value']
			db_api.add_entry(dict_variables['user'], request.form['food_item'],request.form['caloric_value'])


			#list out and display users past entries and related info
			dict_variables['consumption']=db_api.get_todays_entries(dict_variables['user'])

			return render_template('entry_page.html', dict_variables=dict_variables)
		else:
			dict_variables['user']=session.get('username')
			dict_variables['display_message']=True
			dict_variables['message']="Incorrect Entry Format either Food entry or Calorie Entry is not present"
			return render_template('entry_page.html', dict_variables=dict_variables)




if __name__ == '__main__':

	app.secret_key = 'some secret key'
	app.run(host='0.0.0.0', port = 8091)