from flask import render_template, Flask, url_for, redirect, request, session
import os
import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
import traceback
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, DateTime, desc
import datetime
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

app.config['SECRET_KEY'] = 'LATHERAPEUTICS'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///latherapeutics.db'

db=SQLAlchemy(app)

sender = 'prudhvik.1996@gmail.com'
receivers = ['prudhvik.1996@gmail.com']

order_to_la_html = """\
<html>
  <head></head>
  <body>
	<p>
	  Dear LaTherapeutics,<br>
	  Here is the order update from <b>|*order_from*|<b>, <br>
	</p>
	<table style="font-family: arial, sans-serif; border-collapse: collapse; width: 60%;">
	  <tr style="font-weight: bold; background-color: #4242EE; color: white;">
		<td style="text-align: center; border: 1px solid black; text-align: left; padding: 8px;">
		  Product Name
		</td>
		<th style="border: 1px solid black; text-align: left; padding: 8px; width: 30%; text-align: center;">
		  Quantity <br><span style="font-weight: normal; font-size: 14px;">(in Strips / Bottles / Sachets)</span>
		</th>
	  </tr>
	  |*order_rows*|
	</table>

  </body>
</html>
"""
order_from_stockiest_html = """\
<html>
  <head></head>
  <body>
	<p>
	  To,<br>
	  M/s <b>|*stockiest*|</b>,<br>
	  We are in receipt of your order dated |*current_date*| and it will be served shortly..<br>
	</p>
	<table style="font-family: arial, sans-serif; border-collapse: collapse; width: 60%;">
	  <tr style="font-weight: bold; background-color: #4242EE; color: white;">
		<td style="text-align: center; border: 1px solid black; text-align: left; padding: 8px;">
		  Product Name
		</td>
		<th style="border: 1px solid black; text-align: left; padding: 8px; width: 30%; text-align: center;">
		  Quantity <br><span style="font-weight: normal; font-size: 14px;">(in Strips / Bottles / Sachets)</span>
		</th>
	  </tr>
	  |*order_rows*|
	</table>
	<br>
	Thank you,<br><br>
	La Therapeutics,<br>
	+91 82 97 98 99 55,<br>
	Atlanta, Near Soundarya Garden,<br>
	Near WH Bridge, PUNE - 411057.<br><br>
	www.latherapeutics.com<br>
  </body>
</html>
"""
orders_in_email_html = '''
<tr style="font-weight: bold;">
	<td style="text-align: center; border: 1px solid black; text-align: left; padding: 8px;">
		|*product_name*|
	</td>
	<th style="border: 1px solid black; text-align: left; padding: 8px; width: 30%; text-align: center;">
		|*product_qty*| 
		<span style="padding-left: 10px; font-weight: normal; font-size: 16px;">
			|*product_units*|
		</span>
	</th>
</tr>
'''

notify_applicant_for_application = '''
<html>
  <head></head>
  <body>
	<p>
	  To,<br>
	  Mr/Ms <b>|*applicant_name*|</b>,<br>
	  We have recieved your resume and will revert after processing..<br>
	</p>
	<br>
	Thank you,<br><br>
	La Therapeutics,<br>
	+91 82 97 98 99 55,<br>
	Atlanta, Near Soundarya Garden,<br>
	Near WH Bridge, PUNE - 411057.<br><br>
	www.latherapeutics.com<br>
  </body>
</html>
'''

roles = ["Territory Business Manager", "Area Business Manager", "State Business Manager", "Zonal Business Manager", "National Sales Manager", "Accounts Manager", "Marketing Manager", "Product Manager", "Group Product Manager", "Human Resourses Officer", "Business Processing Officer"]

cwd = os.getcwd()

# Stockiest login details
class stockiest_login_details(db.Model):
	__tablename__ = 't_stockiest_login_details'
	__table_args__ = (db.UniqueConstraint('f_user_id', name='unique_user_id_constraint'),)
	f_id = db.Column(db.Integer, primary_key = True)
	f_user_id = db.Column(db.String(100), nullable = False)
	f_email = db.Column(db.String(100), nullable = False)
	f_display_name = db.Column(db.String(200))
	f_password = db.Column(db.String(240))
	f_phone = db.Column(db.String(20))
	f_create_time = db.Column(DateTime(), default=datetime.datetime.now())
	f_last_updated_time = db.Column(DateTime(), default=datetime.datetime.now())

	def __init__(self, f_display_name, f_email, f_password, f_phone, f_create_time = datetime.datetime.now(), f_last_updated_time = datetime.datetime.now()):
		self.f_email = f_email
		self.f_display_name = f_display_name
		self.f_password = f_password
		self.f_phone = f_phone
		self.f_create_time = f_create_time

	def __repr__(self):
		return '<Entry\nEmail Id: %r\nDisplay Name: %r\nPassword: %r\nPhone number: %r\n>' % (self.f_email, self.f_display_name, self.f_password, self.f_phone)

class product_details(db.Model):
	__tablename__ = 't_product_details'
	f_id = db.Column(db.Integer, primary_key = True)
	f_product_name = db.Column(db.String(200), nullable = False)
	f_display_name = db.Column(db.String(100))
	f_product_units = db.Column(db.String(100))
	f_display_caption = db.Column(db.String(1000))
	f_img_url = db.Column(db.String(1000))
	f_status = db.Column(db.String(10), default="active")
	f_create_time = db.Column(DateTime(), default=datetime.datetime.now())
	f_last_updated_time = db.Column(DateTime(), default=datetime.datetime.now())

	def __init__(self, f_product_name, f_display_name, f_product_units, f_display_caption, f_img_url, f_create_time = datetime.datetime.now(), f_last_updated_time = datetime.datetime.now()):
		self.f_product_name = f_product_name
		self.f_display_name = f_display_name
		self.f_product_units = f_product_units
		self.f_display_caption = f_display_caption
		self.f_img_url = f_img_url
		self.f_password = f_password
		self.f_create_time = f_create_time

	def __repr__(self):
		return '''
<Entry>
f_product_name: |f_product_name|
f_display_name: |f_display_name|
f_product_units: |f_product_units|
f_display_caption: |f_display_caption|
f_img_url: |f_img_url|
f_create_time: |f_create_time|
f_last_updated_time: |f_last_updated_time|
'''.replace("|f_product_name|", self.f_product_name).replace("|f_display_name|", self.f_display_name).replace("|f_product_units|", self.f_product_units).replace("|f_display_caption|", self.f_display_caption).replace("|f_img_url|", self.f_img_url).replace("|f_create_time|", str(self.f_create_time)).replace("|f_last_updated_time|", str(self.f_last_updated_time))

db.create_all()

def authenticate_user(user_id, password):
	details = stockiest_login_details.query.filter_by(f_user_id = user_id).all()
	if(len(details)>0):
		if details[0].f_password == password:
			return ""
		else: return "Incorrect Password"
	return "User Id does not exists"

def get_user_email_with_user_id(user_id):
	details = stockiest_login_details.query.filter_by(f_user_id = user_id).all()
	if(len(details)>0):
		return details[0].f_email
	return None

def get_user_display_name_with_user_id(user_id):
	details = stockiest_login_details.query.filter_by(f_user_id = user_id).all()
	if(len(details)>0):
		return details[0].f_display_name
	return None

def send_mail(message, to="latherapeutics@gmail.com"):
	try:
		# creates SMTP session 
		s = smtplib.SMTP('smtp.gmail.com', 587) 
		# start TLS for security 
		s.starttls() 
		# Authentication 
		# s.login("prudhvik.1996@gmail.com", "A*1Lavanya") 
		s.login("latherapeutics@gmail.com", "009160108108") 
		# sending the mail 
		s.sendmail("latherapeutics@gmail.com", to, message) 
		# terminating the session 
		s.quit() 
		print("Successfully sent email")
		return "success"
	except:
		traceback.print_exc()
		return "failed to send email"

@app.route('/', methods=['GET', 'POST'])
def homepage():
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		phone = request.form['phone']
		subject = "Someone from your blog - " + request.form['subject']
		message = request.form['message']
		message = "\n\nEmail: " + email + "\nPhone: " + phone + "\nSubject: " + subject + "\nMessage: " + message + "\n"
		print(name, email, phone, subject, message)
		return send_mail(message)
	else:
		products_list = product_details.query.filter_by(f_status = "active").order_by("f_product_name").all()
		return render_template('homepage.html', products = products_list)

@app.route('/stockiest_portal', methods=['GET'])
def get_stockiest_portal():
	products_list = []
	if session and session['logged_in']:
		products_list = product_details.query.filter_by(f_status = "active").order_by("f_product_name").all()
		for product in products_list:
			print(product.f_display_name)
	return render_template('stockiest_portal.html', products_list=products_list)

@app.route('/stockiest_portal_login', methods=['POST'])
def stockiest_portal_login():
	print("Logging in..")
	session['logged_in'] = False
	
	user_id = request.form['login_user_id']
	password = request.form['login_password']
	
	print(user_id, password)

	login_error = authenticate_user(user_id, password)

	if login_error == "":
		session['logged_in'] = True
		session['user_id'] = user_id
	else:
		login_error = "Invalid User Id or Password"

	print("login_error: " + str(login_error))
	return login_error

@app.route('/stockiest_portal_logout', methods=['POST'])
def stockiest_portal_logout():
	print("Logging out..")
	session['logged_in'] = False
	return ""

@app.route('/make_order', methods=['POST'])
def make_order():
	try:		
		orders = request.form.getlist('orders[]')

		print(orders)
		orders_to_mail = []
		total_orders = 0
		html_orders = []

		for each_order in orders:
			each_order_dict = dict(json.loads(each_order))
			
			if each_order_dict["product_qty"] != "":
				total_orders += int(each_order_dict["product_qty"])
				html_orders.append(orders_in_email_html.replace("|*product_name*|",each_order_dict["product_name"]).replace("|*product_units*|",each_order_dict["product_units"]).replace("|*product_qty*|",each_order_dict["product_qty"]))
				orders_to_mail.append((each_order_dict["product_id"], each_order_dict["product_qty"]))

		if total_orders == 0:
			return "Invalid entry.."

		orders_html = ""

		for each_order_html in html_orders:
			orders_html += each_order_html

		msg_to_la = MIMEMultipart('alternative')
		msg_to_la['Subject'] = "Order alert"

		mail_order_to_la_html = order_to_la_html.replace("|*order_rows*|",orders_html)
		mail_order_to_la_html = mail_order_to_la_html.replace("|*order_from*|",session['user_id'])
		
		html_part = MIMEText(mail_order_to_la_html, 'html')
		msg_to_la.attach(html_part)
		
		send_mail(msg_to_la.as_string())

		msg_to_stockiest = MIMEMultipart('alternative')
		msg_to_stockiest['Subject'] = "Order alert"

		mail_order_to_stockiest_html = order_from_stockiest_html.replace("|*stockiest*|",get_user_display_name_with_user_id(session['user_id'])).replace("|*current_date*|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		mail_order_to_stockiest_html = mail_order_to_stockiest_html.replace("|*order_rows*|",orders_html)

		html_part = MIMEText(mail_order_to_stockiest_html, 'html')
		msg_to_stockiest.attach(html_part)

		send_mail(msg_to_stockiest.as_string(), get_user_email_with_user_id(session['user_id']))
		return "Successfully placed your order.."
	except:
		return "Internal Server Error"

@app.route('/careers_portal', methods=['GET', 'POST'])
def get_careers_portal(application_status = ""):
	try:
		if request.method == 'POST':
			f = request.files['file']  
			applicant_name = request.form['applicant_name']
			applicant_email = request.form['applicant_email']
			applicant_mobile = request.form['applicant_mobile']
			applicant_field = request.form['applicant_field']
			print(applicant_name, applicant_email, applicant_mobile, applicant_field)
			f.save(f.filename)
			print(f.filename)
			
			msg_to_la = MIMEMultipart() 
			msg_to_la['Subject'] = "Job alert"
			html_part = MIMEText("<h3>Job Alert from %r, %r, %r, %r</h3>" %(applicant_name, applicant_email, applicant_mobile, applicant_field), 'html')
			msg_to_la.attach(html_part)
			attachment = open(cwd + "/" + f.filename, "rb")
			p = MIMEBase('application', 'octet-stream') 
			p.set_payload((attachment).read()) 
			encoders.encode_base64(p) 
			p.add_header('Content-Disposition', "attachment; filename= %s" % f.filename) 
			msg_to_la.attach(p) 
			send_mail(msg_to_la.as_string())

			msg_to_applicant = MIMEMultipart('alternative')
			msg_to_applicant['Subject'] = "You Job Application Status"

			html_part = MIMEText(notify_applicant_for_application.replace("|*applicant_name*|", applicant_name), 'html')
			msg_to_applicant.attach(html_part)
			send_mail(msg_to_applicant.as_string(), applicant_email)
			
			return render_template('careers_portal.html', roles = roles, application_status = "Applied successfully!!")
	except:
		return render_template('careers_portal.html', roles = roles, application_status = "Internl Server Error!")
	return render_template('careers_portal.html', roles = roles, application_status = application_status)

if __name__ == '__main__':
	app.run(debug = True, host='192.168.0.105', threaded = True)
