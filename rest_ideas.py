# REST server ideas
from flask import Flask, url_for, request, Response, json, jsonify
from functools import wraps
import logging

# Helper Functions

# Authentication Methods
def check_auth(username, password):
	return username == 'admin' and password == 'password'

# The authentication method - basic http auth
def authenticate():
	message = {'message': 'Authenticate'}
	resp = jsonify(message)

	resp.status_code = 401
	resp.headers['WWW-Authenticate'] = 'Basic realm="tequila.xmission.com"'

	return resp

# require_auth - creates a decorator that forces authentication
def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth:
			return authenticate()
		
		elif not check_auth(auth.username, auth.password):
			return authenticate("Authentication Failed.")
		
		return f(*args, **kwargs)

	return decorated

# Snipet to create a JSON app
__all__ = ['make_json_app']

def make_json_app(import_name, **kwargs):
	"""
	Creates a JSON-oriented Flask app.

	All error responses that you don't specifically
	manage yourself will have application/json content
	type, and will contain JSON like this (just an example):

	{ "message": "405: Method Not Allowed" }
	"""
	def make_json_error(ex):
		response = jsonify(message=str(ex))
		response.status_code = (ex.code
						if isinstance(ex, HTTPException)
						else 500)
		return response

	app = Flask(import_name, **kwargs)

	for code in default_exceptions.iterkeys():
		app.error_handler_spec[None][code] = make_json_error

	return app

# Flask Application
app = Flask(__name__)

# setup logging
file_handler = logging.FileHandler('app.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# A blank route for a homepage/default action
@app.route('/')
def api_root():
	return "Welcome"

# A standard route
@app.route('/articles')
def api_articles():
	return "List of " + url_for('api_articles')

# A route with a parameter
# Various types of converters for a parameter
#@app.route('/articles/<int:articleid>')
#@app.route('/articles/<float:articleid>')
#@app.route('/articles/<path:articleid>')
@app.route('/articles/<articleid>')
def api_article(articleid):
	return 'You are reading article: ' + articleid

# Route with some request argument foo
@app.route('/hello')
def api_hello():
	if 'name' in request.args:
		return 'Hello ' + request.args['name']
	else:
		return "Hello - add name arg to be personal"

# Various types of http verbs
@app.route('/echo', methods = [
	'GET', 'POST', 'PATCH', 'PUT', 'DELETE'
	])
def api_echo():
	if request.method == 'GET':
		return "ECHO: GET\n"
	elif request.method == 'POST':
		return "ECHO: POST\n"

	elif request.method == 'PATCH':
		return "ECHO: PACTH\n"

	elif request.method == 'PUT':
		return "ECHO: PUT\n"

	elif request.method == 'DELETE':
		return "ECHO: DELETE\n"

# Response data
@app.route('/hello_world', methods = [ 'GET' ])
def api_hello_world():
	data = {
		'hello': 'world',
		'number': 3
	}
	js = json.dumps(data)

	#resp = Response(js, status=200, mimetype='application/json')
	resp = jsonify(data)
	resp.status_code = 200
	resp.headers['Link'] = 'http://www.xmission.com'

	return resp

# Routing 404 errors
@app.errorhandler(404)
def not_found(error=None):
	message = {
			'status': 404,
			'message': 'Not Found: ' + request.url,
			}
	resp = jsonify(message)
	resp.status_code = 404

	return resp

# Demo routing values + errors
@app.route('/users/<userid>', methods=['GET'])
def api_users(userid):
	users = {'1':'joe', '2':'steve', '3':'bob'}

	if userid in users:
		return jsonify({userid:users[userid]})
	else:
		return not_found()

# Demo authentication
@app.route('/secrets')
@requires_auth
def api_hello():
	return "Secret!"

@app.route('/logging_test')
def api_logging_test():
	app.logger.info('Information')
	app.logger.warning('Warning')
	app.logger.error('Error')

	return "Check the logs!\n"
	
# The main app run, plus authentication mode
if __name__ == '__main__':
	app.debug = True
	app.run()

