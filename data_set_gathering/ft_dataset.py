import os
import openai
from dotenv import load_env
import pandas as pd
import time

'''
Please note that this file has not been tested individually yet.
'''

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# The Davinci model is currently used in this file. Please note that while this is the 
#	most powerful model with the largest amount of accepted tokens, it is also the slowest and most expensive.
QA_GENERATING_MODEL = 'text-davinci-003'

PROMPT_SUFFIX = '\n\n###\n\n'
COMPLETION_STOPPING = '\n==++==\n'

'''
Decorator function for rate limit exponential delay
Done as a measure to prevent RateLimitErrors from occurring during runs
'''
def ratelimiterror_exponential_backoff(
    func,
    init_delay=60,
    expo_base=2,
    errors=(openai.error.RateLimitError),
    max_retries=5
):
    def wrapper(*args, **kwargs):
        retries = 0
        delay = init_delay
        while True:
            try:
                return func(*args, **kwargs)
            except errors as e:
                retries += 1
                if retries > max_retries:
                    raise Exception(f'Exceeded maximum number of retries ({max_retries})')
                    
                print(f'RateLimitError: Sleeping for {delay} seconds')
                time.sleep(delay)
                delay *= expo_base
                print(f'Next error wait time is {delay} seconds. {max_retries - retries} retries remaining')
                
                
            except Exception as e:
                raise e
    return wrapper

'''
Uses a GPT-3 model to:
- generate questions based on the articles
- generate answers to the generated questions given the articles
- construct a dataset that contains the articles and questions as prompts,
	and the answers as completions

'''
def generate_qa_finetune_dataset(workbook_file, save_to='qa_ft_dataset'):
	articles = pd.read_excel(workbook_file)
	# split long articles into shorter chunks
	dataset = get_trimmed_articles(articles)
	# use GPT-3 to generate questions for each piece of content
	dataset['questions'] = dataset['content'].apply(generate_questions)
	# use GPT-3 to generate answers for the previously generated questions
	dataset['answers'] = dataset.apply(lambda row: generate_answers(row['content'], row['questions']), axis=1)
	# sanitize the content, questions, and answers to follow OpenAI prompt-completion formatting rules
	dataset['prompt'] = dataset.apply(lambda row: generate_ft_prompt(row['content'], row['questions']), axis=1)
	dataset['completion'] = dataset['answers']
	
	# save all to CSV
	dataset.to_csv(save_to + '.csv')
	# save prompt-completions to JSONL ready to be sent for fine-tuning
	dataset[['prompt', 'completion']].to_json(save_to + 'jsonl', orient='records', lines=True)
	

'''
Accepts a DataFrame of articles, and returns a new DataFrame with 
	article contexts not much longer than 4000 characters.
Done as a measure to make sure requests stay within model token limits
'''
def get_trimmed_articles(df):
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
	
	resp = articles.apply(lambda row: split_article(row['title'], row['date_published'], row['timeout'], row['content']), axis=1)
	return resp.melt(value_name='content').drop('variable', axis=1).dropna()

'''
Calls GPT-3 to generate a questions from the given context.
Currently, it will generate 3 questions.
'''
@ratelimiterror_exponential_backoff
def generate_questions(context):
    wait_time = 3.5
    response = openai.Completion.create(
        model=QA_GENERATING_MODEL,
        prompt=f'Write three questions based on the article below\nArticle: {context}\nQuestions:\n1.',
        presence_penalty=0.5,
        frequency_penalty=0.5,
        temperature=1,
        top_p=1,
        max_tokens=750,
        stop=['\n\n']
    )
    time.sleep(wait_time)
    questions = '1.' + response['choices'][0]['text']
    return questions

'''
Calls GPT-3 to answer the questions given the context.
'''
@ratelimiterror_exponential_backoff
def generate_answers(context, questions):
    wait_time = 3.5
    response = openai.Completion.create(
        model=QA_GENERATING_MODEL,
        prompt=f'Write answers to the questions based on the article below\nQuestions:\n{questions}\n\nArticle: {context}\n\nAnswers:\n1.',
        presence_penalty=0.5,
        frequency_penalty=0.5,
        temperature=1,
        top_p=1,
        max_tokens=750,
    )
    time.sleep(wait_time)
    answers = '1.' + response['choices'][0]['text']
    return answers

'''
Formats the context-questions to prompts according to OpenAI's formatting guidelines
'''
def generate_ft_prompt(context, questions):
    return f'{questions}\n\nArticle: {context}{PROMPT_SUFFIX}'

'''
Formats the answers to completions according to OpenAI's formatting guidelines
'''
def generate_ft_completion(answer):
    return f' {answer}{COMPLETION_STOPPING}'

