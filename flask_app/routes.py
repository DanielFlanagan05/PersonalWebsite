# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
	if 'email' in session:
		encrypted_email = session['email']
		email = db.reversibleEncrypt('decrypt', encrypted_email)
		return email
	else:
		return 'Unknown'

@app.route('/login')
def login():
	return render_template('login.html', user = getUser())

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/')

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
	# Get the email and password from the data element of the AJAX POST
	email = request.form.get('email')
	password = request.form.get('password')
	
	auth_result = db.authenticate(email, password)
	
	if auth_result['success']:
		session['email'] = db.reversibleEncrypt('encrypt', email) 
		return json.dumps({'success':1})
	else:
        # If authentication fails because user is not found, create a new user
		if auth_result['message'] == 'User not found':
			create_result = db.createUser(email, password)
			if create_result['success']:
				# Log in the newly created user
				session['email'] = db.reversibleEncrypt('encrypt', email)
				return json.dumps({'success': 1})
			else:
				# user creation failed
				return json.dumps({'success': 0, 'error': 'User creation failed'})     
		else:
			# Authenticcation failure for a reason other than user not found        
			return json.dumps({'success': 0})

	# form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
	# session['email'] = form_fields['email']
	# return json.dumps({'success':1})


#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())

@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    if getUser() == 'owner@email.com':
        emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
        emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:grey;text-align: left'}, room='main')

@socketio.on('message', namespace='/chat')
def message(data):
    if getUser() == 'owner@email.com':
        emit('message', { 'msg': data['message'], 'style': 'width: 100%;color:blue;text-align: right', 'sender':'owner' }, room='main')
    else:
        emit('message', { 'msg': data['message'], 'style': 'width: 100%;color:grey;text-align: left', 'sender':'user' }, room='main')

@socketio.on('leave', namespace='/chat')
def left(message):

    leave_room('main')
    if getUser() == 'owner@email.com':
        emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
        emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:grey;text-align: left'}, room='main')

#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	print(db.query('SELECT * FROM users'))
	x = random.choice(['I\'ve been to 1 of the 4 green sand beaches in the world','I design and print 3D models','I own a tablet with a GPU'])
	return render_template('home.html', user=getUser(), fun_fact = x)

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

#######################################################################################
# Copied in from HW2. Unsure if routing from static/<path:path> should replace this, but links didn't work so pasting these in
#######################################################################################

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	pprint(resume_data)
	return render_template('resume.html', resume_data = resume_data, user = getUser())

@app.route('/projects')
def projects():
	return render_template('projects.html', user = getUser())

@app.route('/piano')
def piano():
	return render_template('piano.html', user = getUser())

@app.route('/processfeedback', methods=['POST'])
def process_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    comment = request.form.get('comment')
    
    insert_query = "INSERT INTO feedback (name, email, comment) VALUES (%s, %s, %s)"
    db.query(insert_query, [name, email, comment])
    
    feedback_query = "SELECT * FROM feedback"
    feedback_list = db.query(feedback_query)
    
    return render_template('processfeedback.html', feedback_list=feedback_list, user = getUser())