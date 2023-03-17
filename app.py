import configparser
from flask import Flask, render_template, request, jsonify
from app_helper import ModelController

app = Flask(__name__)
app.config.from_object('config')
controller = ModelController()

conversation = []

@app.route('/')
def index():
	return render_template('index.html', model_name=app.config['GPT_MODEL'])

@app.route('/process_question', methods=['POST', 'GET'])
def process_question():
	if request.method == 'POST':
		req_params = request.get_json()
		
		question = req_params.get('question', '')
		ksim = req_params.get('ksim', 1)
		memory = req_params.get('memory', 0)
		refine = req_params.get('refine', 'list')
		
		answer = get_model_response(question, ksim=ksim, memory=memory, refine=refine)
		
		conversation.append({'question': question, 'answer': answer})
		
		return jsonify({'question': question, 'answer': answer})

def get_model_response(
		question,
		ksim=1,
		memory=0,
		refine='list',
	):
	prev_questions = conversation[:-memory]
	return controller.ask_question(app.config['ENDPOINT'], app.config['GPT_MODEL'], question, ksim=ksim, memory=prev_questions, refine=refine)

if __name__ == '__main__':
	app.run(debug=True)
