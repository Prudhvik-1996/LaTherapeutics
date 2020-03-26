from flask import render_template, Flask, url_for, redirect, request
from flask_mail import Mail, Message
import os

app = Flask(__name__)

mail_settings = {
	"MAIL_SERVER": 'smtp.gmail.com',
	"MAIL_PORT": 465,
	"MAIL_USE_TLS": False,
	"MAIL_USE_SSL": True,
	# Enable this for Dev
	"MAIL_USERNAME": 'prudhvik.1996@gmail.com',
	"MAIL_PASSWORD": 'A*1lavanya'
	# Enable this for Prod
	# "MAIL_USERNAME": 'prudhvik.1996@msitprogram.net',
	# "MAIL_PASSWORD": 'msit12345'
}

app.config.update(mail_settings)
mail = Mail(app)

app.config['SECRET_KEY'] = 'PRUDHVIK'

@app.route('/', methods=['GET', 'POST'])
def homepage():
	if request.method == 'POST':
		name = request.form['Name']
		email = request.form['Email']
		phone = request.form['Phone']
		subject = "Someone from your blog - " + request.form['Subject']
		message = request.form['Message'] + "\n\nEmail: " + email + "\n\nPhone: " + phone
		print(name, email, phone, subject, message)
		with app.app_context():
			msg = Message(
				sender=email,
				recipients=["prudhvik.1996@gmail.com"],
				subject = subject,
				body=message
			)
			mail.send(msg)
		# return render_template('index.html', contactMeMessage = "success")
	else:
		return render_template('index.html', contactMeMessage = "")

if __name__ == '__main__':
	app.run(debug = True)
