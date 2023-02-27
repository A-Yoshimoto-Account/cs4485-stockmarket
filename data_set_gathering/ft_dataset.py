import pandas as pd
import numpy as np
import re

import openai_qa_helper
import embeddings_helper

RANDOM_QUESTION_LIST = [
	"What's your favorite color?",
	"Do you like music?",
	"Do you have any pets?",
	"What's your favorite movie?",
	"Can you tell me a joke?",
	"What's your favorite book?",
	"Do you believe in aliens?",
	"What's your favorite food?"
    "What's the weather like today?",
	"Do you like to travel?",
	"Can you tell me a fun fact?",
	"What's your favorite type of art?",
	"Do you believe in love at first sight?",
	"What's your favorite type of music?",
	"Do you have any hobbies?"
]
PHRASE_BLACKLIST = ['read on', 'click the', 'check out the video', 'watch the video']

COL_CONTEXT = 'context'
COL_QUESTION = 'questions'
COL_ANSWER = 'answers'
PROMPT_SUFFIX = '\n\n###\n\n'
COMPLETION_STOPPING = '\n==++==\n'

'''
Uses a GPT-3 model to:
- generate questions based on the articles
- generate answers to the generated questions given the articles
- construct a dataset that contains the articles and questions as prompts,
	and the answers as completions

'''
def generate_qa_finetune_dataset(df, save_to='qa_ft_dataset', contexts_csv='contexts.csv', embed_csv='embeddings.csv', debug=False):
	try:
		# perform dataset cleaning, like filtering articles with bad phrases and replacing double newlines
		df = clean_df(df)
		if debug:
			print('Filtered and cleaned articles')
		# split long articles into shorter chunks
		contexts = get_contexts(df)
		if debug:
			print('Trimmed articles')
		# get embeddings for each trimmed article
		context_embeddings = get_context_embeddings(contexts)
		if debug:
			print('Obtained article embeddings')
		# use GPT-3 to generate questions for each piece of content
		questions_dataset = generate_questions(contexts)
		if debug:
			print('Generated questions')
			print(f'{questions_dataset.isnull().sum(axis=1)} rows without generations (will be removed from here on)')
		questions_dataset.dropna(inplace=True)
		
		# use GPT-3 to generate answers for the previously generated questions
		qa_dataset = generate_answers(questions_dataset)
		if debug:
			print('Generated answers')
			print(f'{qa_dataset.isnull().sum(axis=1)} rows without generations (will be removed from here on)')
		qa_dataset.dropna(inplace=True)
		
		# add random content-question-answer pairs, and add random questions to train for IDK cases
		idk_cases = get_idk_cases(qa_dataset, contexts, context_embeddings)
		training_dataset = pd.concat([qa_dataset, idk_cases])
		training_dataset.reset_index(drop=True)
		if debug:
			print('Created IDK cases')
		# sanitize the content, questions, and answers to follow OpenAI prompt-completion formatting rules
		training_dataset['prompt'] = training_dataset.apply(lambda row: generate_ft_prompt(row[COL_CONTEXT], row[COL_QUESTION]), axis=1)
		training_dataset['completion'] = training_dataset[COL_ANSWER]
		if debug:
			print('Created full training dataset')
			print('Saving dataset and fine-tune JSONL')
		
		# save original trimmed articles and embeddings
		contexts.to_csv(contexts_csv, index=False)
		context_embeddings.to_csv(embed_csv, index=False)
		# save all to CSV
		training_dataset.to_csv(save_to + '.csv', index=False)
		# save prompt-completions to JSONL ready to be sent for fine-tuning
		training_dataset[['prompt', 'completion']].to_json(save_to + '.jsonl', orient='records', lines=True)
		
		return True
	except Exception as e:
		print(type(e).__name__, e)
		return False

'''
Accepts a DataFrame of articles, and returns a new DataFrame with 
	article contexts not much longer than 4000 characters.
Done as a measure to make sure requests stay within model token limits
'''
def get_contexts(df, title_col='title', date_col='date_published', timeout_col='timeout', content_col='content'):
	def split_article(title, date, timeout, content):
		if timeout:
			return None
		header = f'{title}\n{date}\n'
		prompts = []
		divs = len(content) // 4000
		for _ in range(divs):
			div = ''
			while len(div) < 4000:
				newline_index = content.find('\n')
				cut = content[:newline_index]
				div += cut + '\n'
				content = content[newline_index + 1:]
			
			prompts.append(header + div)
		prompts.append(header + content)
		return pd.Series(prompts)
	
	resp = df.apply(lambda row: split_article(row[title_col], row[date_col], row[timeout_col], row[content_col]), axis=1)
	resp = resp.melt(value_name=COL_CONTEXT).drop('variable', axis=1).dropna()
	return resp.reset_index(drop=True)

def clean_df(df, col_context='content'):
	df = df[df[col_context].map(content_filter) == False]
	#df[col_context] = df[col_context].apply(remove_double_newlines)
	return df
	
def content_filter(text):
	for phrase in PHRASE_BLACKLIST:
		if phrase in text:
			return True
	return False

def remove_double_newlines(text):
	return text.replace('\n\n', '\n')

def get_context_embeddings(dataset):
	return openai_qa_helper.model_get_embeddings(dataset[COL_CONTEXT].tolist())

def generate_questions(dataset):
	question_dfs = dataset[COL_CONTEXT].apply(openai_qa_helper.model_get_questions)
	df = pd.concat(list(question_dfs))
	df[COL_QUESTION] = df[COL_QUESTION].apply(lambda question: question.strip(' \n\t'))
	return df

def generate_answers(dataset):
	dataset[COL_ANSWER] = dataset.apply(lambda row: openai_qa_helper.model_get_answers(row[COL_CONTEXT], row[COL_QUESTION]), axis=1)
	dataset[COL_ANSWER] = dataset[COL_ANSWER].apply(lambda question: question.strip(' \n\t'))
	# may need to remove phrases such as 'Based on the article,'
	return dataset

'''
Generates IDK cases
'''
def get_idk_cases(qa_dataset, contexts, embeddings, random=True, unrelated=True, related=False, random_prob=0.3, unrelated_prob=0.5, related_prob=0.2):
	idk_cases = []
	for i, row in qa_dataset.iterrows():
		question = row[COL_QUESTION]
		q_context = row[COL_CONTEXT]
		if related:
			if np.random.random() < related_prob:
				related_context = embeddings_helper.get_related_contexts(i, contexts, embeddings, 5)
				related = np.random.choice(related_context)
				idk_cases.extend({
							COL_CONTEXT: related,
							COL_QUESTION: question,
							COL_ANSWER: 'I couldn\'t find the relevant context to answer the question.'
						})
		if unrelated:
			if np.random.random() < unrelated_prob:
				unrelated_context = embeddings_helper.get_related_contexts(i, contexts, embeddings, 5, reverse=True)
				unrelated = np.random.choice(unrelated_context)
				idk_cases.append({
							COL_CONTEXT: unrelated,
							COL_QUESTION: question,
							COL_ANSWER: 'I couldn\'t find the relevant context to answer the question.'
						})
		if random:
			if np.random.random() < random_prob:
				random_question = np.random.choice(RANDOM_QUESTION_LIST)
				idk_cases.append({
							COL_CONTEXT: q_context,
							COL_QUESTION: random_question,
							COL_ANSWER: 'I couldn\'t find the relevant context to answer the question.'
						})
	return pd.DataFrame(idk_cases)

'''
Formats the context-questions to prompts according to OpenAI's formatting guidelines
'''
def generate_ft_prompt(context, questions):
    return f'{questions}\n\nContext: {context}{PROMPT_SUFFIX}'

'''
Formats the answers to completions according to OpenAI's formatting guidelines
'''
def generate_ft_completion(answer):
    return f' {answer}{COMPLETION_STOPPING}'

