from flask import Flask, render_template, request, redirect

app = Flask(__name__)

questions = []
answers = []

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		question = request.form.get('question')
		questions.append(question)
		answers.append(get_model_response(question))
		return redirect(request.path)
	if request.method == 'GET':
		return render_template('index.html', questions=questions, answers=answers, zip=zip)

def get_model_response(question):
	return 'placeholder text'

if __name__ == '__main__':
	app.run()
