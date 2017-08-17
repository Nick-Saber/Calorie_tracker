from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, Column, Table, ForeignKey, func
from sqlalchemy import Integer, String, DateTime, cast, Date
from sqlalchemy.orm import sessionmaker as sm 
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import label
import datetime

engine = create_engine("postgresql://NickAccount:@localhost/calorie_tracker",echo=True)

Base=declarative_base()
db_session=sm(bind=engine)

class user(Base):
	__tablename__='users'

	username=Column(String, primary_key=True)
	password=Column(String)

	def __init__(self, username,password):
		self.username=username
		self.password=password

class food_entries(Base):
	__tablename__='food_entries'

	entry_id=Column('entry_id',Integer,Sequence("food_entries_sequence", start=1,increment=1),primary_key=True)
	foodname=Column(String)
	caloric_value=Column(Integer)
	entry_date=Column(DateTime, default = func.current_timestamp())
	username=Column(String, ForeignKey(user.username))

	def __init__(self,foodname,caloric_value,username):
		self.foodname=foodname
		self.caloric_value=caloric_value
		self.username=username


Base.metadata.create_all(engine)

#Functin that checks if a username exists and if so if the password is correct
def check_login(login_name,pswd):
	current_sesh = db_session()
	result = current_sesh.query(user).get(str(login_name))
	current_sesh.close()
	if(result):
		if(result.password==pswd):
			return (True, "Login Succesful")
		else:
			return (False, "Password is incorrect")
	else:
		return (False, ("User %s does not exist Please Make an account" % login_name))


#Adds new users to the database
def add_user(username,password):
	current_sesh = db_session()
	current_sesh.add(user(username,password))
	try:
		current_sesh.commit()
		committed=True
	except:
		committed=False
	current_sesh.close()
	return committed

#adds new food entries to the database
def add_entry(user, foodname,calories):
	current_sesh = db_session()
	current_sesh.add(food_entries(foodname,calories,user))
	try:
		current_sesh.commit()
		committed=True
	except:
		committed=False
	current_sesh.close()
	return committed

#Gets all the entries a user input today
def get_todays_entries(user):
	current_sesh = db_session()
	result = current_sesh.query(food_entries).filter(food_entries.username =='{}'.format(user)).filter(cast(food_entries.entry_date,Date) == datetime.datetime.today().date())
	sum=0
	#food_entries.entry_date.date() == datetime.datetime.today().date(), 
	for entry in result.all():
		print(str(entry.entry_date.date()== datetime.datetime.today().date()))
		sum+= entry.caloric_value
	current_sesh.close()
	return sum


def get_past_x_days(user,x):
	current_sesh=db_session()
	if x > 20:
		x=20
	elif x< 1:
		x=1
	consumption=current_sesh.query(label('date',func.date(food_entries.entry_date)),label('caloric_consumption',func.sum(food_entries.caloric_value))).group_by(func.date(food_entries.entry_date)).order_by('date').limit(x)
	calories=[]
	dates=[]
	for total in consumption:
		calories.append(total.caloric_consumption)
		dates.append(total.date)
	return [calories,dates]
	
