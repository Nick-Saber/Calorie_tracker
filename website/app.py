from flask import Flask, render_template, url_for, request, redirect, session
import psycopg2 as psql
from psycopg2.extensions import AsIs, QuotedString
import json
import bleach


# from flask.ext.sqlalchemy import SQLAlchemy
import os
secret_key = os.urandom(24)

app = Flask(__name__)

#SQL_alchemy stuff
# app.config.from_pyfile('config.py')
# db=SQL_Alchemy(app)

# class entries(db.model):

# 	food_name=db.Column(db.string(100))
# 	calories=db.Column(db.Integer)
# 	user_name=db.Column(db.string(100))

# 	def __init__(self, food_name,calories,user_name):
# 		self.food_name=food_name
# 		self.calories=calories
# 		self.user_name=user_name




db_name='calorie_tracker'

def add_food_entry(food,caloric_value,user):
	db=psql.connect(dbname=db_name)
	curs=db.cursor()
	curs.execute('INSERT INTO entries (food_name, calories, user_name) VALUES (%s,%s,%s);', (bleach.clean(food),caloric_value,bleach.clean(user)))
	db.commit()
	db.close()

def get_todays_entries(user):
	db=psql.connect(dbname=db_name)
	curs=db.cursor()
	curs.execute('SELECT entries.food_name, entries.calories FROM entries WHERE entries.user_name=%s and entries.day=current_date;', (bleach.clean(user),))
	entries=[{'food':str(row[0]),'calories':int(row[1]) } for row in curs.fetchall()]
	db.close()
	return entries

def get_caloric_consumption(user,date=None):
	db=psql.connect(dbname=db_name)
	curs=db.cursor()
	if date == None:
		curs.execute("""SELECT entries.food_name, entries.calories FROM entries WHERE entries.user_name=%s and entries.day=current_date;""", (bleach.clean(user),))
	else:
		curs.execute("""SELECT entries.food_name, entries.calories FROM entries WHERE entries.user_name=%s and entries.day=date;""", (bleach.clean(user),bleach.clean(date),))

	entries=[{'food':str(row[0]),'calories':int(row[1]) } for row in curs.fetchall()]
	db.close()
	consumption=0
	for item in entries:
		consumption=consumption + item['calories']
	return consumption

def get_past_x_days_cc(user,days=7):
	db=psql.connect(dbname=db_name)
	curs=db.cursor()
	curs.execute("""SELECT SUM(entries.calories), entries.day FROM entries WHERE entries.user_name=%s GROUP BY entries.day ORDER BY entries.day DESC;""", (bleach.clean(user),))
	entries=[row for row in curs.fetchmany(days)]
	db.close()
	return entries





@app.route('/' methods= ['GET','POST'])
def login():
	dict_variables={}
	dict_variables['user']=session.get('username')
	return render_template('login.html' , dict_variables=dict_variables)



@app.route('/entry_page', methods=['GET','POST'] )
def entry_page():
	dict_variables={}
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
			add_food_entry(request.form['food_item'],request.form['caloric_value'],dict_variables['user'])


			#list out and display users past entries and related info
			dict_variables['entries']=get_todays_entries(dict_variables['user'])
			dict_variables['display_entries']=True
			dict_variables['consumption']=get_caloric_consumption(dict_variables['user'])

			#plot users past history data
			history_data=get_past_x_days_cc(user=dict_variables['user'])
			dict_variables['caloric_history_values']=json.dumps(reverse([entry[0] for entry in history_data])
			dict_variables['caloric_history_dates']=json.dumps([entry[1].__str__() for entry in history_data ])
			dict_variables['history_length'] = len(history_data)


			return render_template('entry_page.html', dict_variables=dict_variables)
		else:
			dict_variables['user']=session.get('username')
			dict_variables['display_message']=True
			dict_variables['message']="Incorrect Entry Format either Food entry or Calorie Entry is not present"
			return render_template('entry_page.html', dict_variables=dict_variables)




if __name__ == '__main__':
	app.secret_key = 'some secret key'
	app.run(host='0.0.0.0', port = 8091)