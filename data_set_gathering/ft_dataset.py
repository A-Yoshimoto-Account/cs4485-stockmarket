import os
import openai
from dotenv import load_env
import pandas as pd

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

'''
Uses a GPT-3 model to:
- generate questions based on the articles
- generate answers to the generated questions given the articles
- construct a dataset that contains the articles and questions as prompts,
	and the answers as completions

'''
def generate_qa_finetune_dataset(workbook_file):
	articles = pd.read_excel(workbook_file)
	articles = trim_articles(articles)
	articles['questions'] = articles['prompt'].apply(generate_questions)
	articles['answers'] = articles.apply(lambda row: generate_answers(row['prompt'], row['questions']), axis=1)
	
	articles['prompt'] = articles.apply(lambda row: generate_prompt(row['prompt'], row['question']), axis=1)
	articles['completion'] = articles['answers']
	pd.to_csv('qa_ft_dataset')

# wrapper for rate limit exponential delay
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

@ratelimiterror_exponential_backoff
def generate_questions(prompt):
    prompt = trim_text(prompt)
    wait_time = 3.5
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=f'Write questions based on the article below\nArticle: {prompt}\nQuestions:\n1.',
        presence_penalty=0.5,
        frequency_penalty=0.5,
        temperature=1,
        top_p=1,
        n=3
    )
    time.sleep(wait_time)
        
    questions = '1.' + response['choices'][0]['text']
    #print(questions)
    return questions

@ratelimiterror_exponential_backoff
def generate_answers(context, questions):
    context = trim_text(context)
    wait_time = 3.5
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=f'Write answers to the questions based on the article below\nQuestions:\n{questions}\n\nArticle: {context}\n\nAnswers:\n1.',
        presence_penalty=0.5,
        frequency_penalty=0.5,
        temperature=1,
        top_p=1,
        stop=['\n\n']
    )
    time.sleep(wait_time)
    
    answers = '1.' + response['choices'][0]['text']
    return '1.' + answers

def generate_ft_prompt(context, questions):
    return f'Write answers to the questions based on the article below\nQuestions:\n{questions}\n\nArticle: {context}\n\nAnswers:\n1.'
