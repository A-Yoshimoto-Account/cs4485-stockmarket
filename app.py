import configparser
from flask import Flask, render_template, request, jsonify
from app_helper import ModelController

app = Flask(__name__)
app.config.from_object('config')
controller = ModelController(app.config['DISABLE_EMBEDDINGS'], app.config['DISABLE_COMPLETIONS'])

conversation = []

@app.route('/')
def index():
	return render_template('index.html', model_name=app.config['GPT_MODEL'])

@app.route('/process_question', methods=['POST', 'GET'])
def process_question():
	if request.method == 'POST':
		req_params = request.get_json()
		
		question = req_params.get('question', '')
		ksim = int(req_params.get('ksim', 1))
		memory = int(req_params.get('memory', 0))
		
		answer = get_model_response(question, ksim=ksim, memory=memory, refine=app.config['REFINE'])
		
		conversation.append({'question': question, 'answer': answer})
		
		return jsonify({'question': question, 'answer': answer})

def get_model_response(
		question,
		ksim=1,
		memory=0,
		refine=None,
	):
	prev_questions = conversation[:-memory]
	return controller.ask_question(app.config['ENDPOINT'], app.config['GPT_MODEL'], question, ksim=ksim, memory=prev_questions, refine=refine)

if __name__ == '__main__':
	app.run(debug=True)
