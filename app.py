from flask import render_template, Flask, url_for, redirect, request
import os
import smtplib
import traceback

app = Flask(__name__)

app.config['SECRET_KEY'] = 'PRUDHVIK'

sender = 'prudhvik.1996@gmail.com'
receivers = ['prudhvik.1996@gmail.com']


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
		try:
			# creates SMTP session 
			s = smtplib.SMTP('smtp.gmail.com', 587) 
			  
			# start TLS for security 
			s.starttls() 
			  
			# Authentication 
			# s.login("prudhvik.1996@gmail.com", "A*1Lavanya") 
			s.login("latherapeutics@gmail.com", "009160108108") 

			# sending the mail 
			s.sendmail("latherapeutics@gmail.com", "latherapeutics@gmail.com", message) 

			# terminating the session 
			s.quit() 

			print("Successfully sent email")
			return "success"
		except:
			traceback.print_exc()
			return "failed to send email"
		return "success"
	else:
		return render_template('index.html', contactMeMessage = "")

if __name__ == '__main__':
	app.run(debug = True)
