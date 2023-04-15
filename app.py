import configparser
import copy

from flask import Flask, render_template, request, jsonify
from app_helper import ModelController
import csv
from io import StringIO

app = Flask(__name__)
app.config.from_object('config')
controller = ModelController(app.config['DISABLE_EMBEDDINGS'], app.config['DISABLE_COMPLETIONS'])

conversation = []


@app.route('/')
def index():
	return render_template('index.html', model_name=app.config['GPT_MODEL'])


#Part of Submit function
# First endpoint to be called when user submits a question
@app.route('/post_user_question', methods=['POST', 'GET'])
def post_user_question():
    if request.method == 'POST': 
        req_params: dict = request.get_json()
        question = req_params.get('question', '')
        return jsonify({'question': question})
    
# Second endpoint to be called after user question posts to UI
@app.route('/process_question', methods=['POST', 'GET'])
def process_question():
	if request.method == 'POST':
		req_params: dict = request.get_json()
		
		question = req_params.get('question', '')
		ksim = int(req_params.get('ksim', 1))
		memory = int(req_params.get('memory', 0))
		answer = ''
		error = ''
		try:
			answer = get_model_response(question, ksim=ksim, memory=memory, refine=app.config['REFINE'])
		except Exception as e:
			print(type(e).__name__)
			print(e)
			answer = 'Unable to get answer'
			error = f'{type(e).__name__} was thrown.'
			if hasattr(e, 'message'):
				error += f' Message: {e.message}'
		
		conversation.append({'question': question, 'answer': answer})
		resp = {'answer': answer}
		if error:
			resp['error'] = error
		return jsonify(resp)


@app.route('/upload_convo', methods=['POST'])
def upload_convo():
	'''
	Receives textual data and parses it as a CSV.
	Overwrites the conversation global list with the CSVs contents, if successful.
	Returns a JSON object containing a message type, a message, and a boolean indicating success/failure.
	'''
	global conversation
	req_params = request.get_json()

	mesg_type = ''
	message = ''
	ok = True
	content = []
	
	buffer = StringIO(req_params)
	try:
		reader = csv.reader(buffer, quotechar='"', escapechar='\\', delimiter=',')
		for row in reader:
			if (len(row) != 2):
				raise Exception
			content.append({
				'question': row[0],
				'answer': row[1]
			})
		mesg_type = 'notification'
		message = 'Conversation memory overwritten with uploaded file'
		ok = True
		conversation = copy.deepcopy(content)
	except:
		mesg_type = 'error'
		message = 'File should be a CSV with no header, with every row following format: "query,response"'
		ok = False
		content = []
	
	# print(conversation)

	return jsonify({
		'type': mesg_type,
		'message': message,
		'ok': ok,
		'content': content
	})


def get_model_response(
		question,
		ksim=1,
		memory=0,
		refine=None,
	):
	prev_questions = conversation[-memory:]
	return controller.ask_question(app.config['ENDPOINT'], app.config['GPT_MODEL'], question, ksim=ksim, memory=prev_questions, refine=refine)

#Clear Conversation Memory Function
@app.route('/clear_memory', methods=['POST', 'GET'])
def clear_memory():
	if request.method == 'POST':
		conversation.clear()
		return "Completed Task"

if __name__ == '__main__':
	app.run(debug=True)
