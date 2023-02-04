from flask import Flask, render_template, request, redirect, jsonify, url_for

app = Flask(__name__)

questions = []
answers = []

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/process_question', methods=['POST', 'GET'])
def process_question():
	if request.method == 'POST':
		question = request.get_json()['question']
		answer = get_model_response(question)
		return jsonify({'question': question, 'answer': answer})

def get_model_response(question):
	return 'placeholder text'

if __name__ == '__main__':
	app.run()
