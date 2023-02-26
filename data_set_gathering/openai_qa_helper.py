import os
from dotenv import load_dotenv
import openai
import pandas as pd
import numpy as np
import time

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


# Curie is used currently due to free-tier and funding limitations
QA_GENERATING_MODEL = 'text-curie-001'
TEXT_EMBEDDINGS_MODEL = 'text-embedding-ada-002'
WAITING_TIME = 3.5

COL_CONTEXT = 'context'
COL_QUESTION = 'questions'
COL_ANSWER = 'answers'

'''
Decorator function for error handling requests to the OpenAI API
Done as a measure to prevent errors from disrupting large contiguous access to the API
'''
def openai_error_handler(
    func,
    init_delay=60,
    expo_base=2,
    ratelimiterror=(openai.error.RateLimitError),
    servererror=(openai.error.APIError, openai.error.Timeout),
    invalidreq=(openai.error.InvalidRequestError),
    rle_max_retries=5,
    servererr_max_retries=5,
):
    def wrapper(*args, **kwargs):
        rle_retries = 0
        servererr_retries = 0
        delay = init_delay
        while True:
            try:
                return func(*args, **kwargs)
            except ratelimiterror as e:
                rle_retries += 1
                if rle_retries > rle_max_retries:
                    raise Exception(f'Exceeded maximum number of retries ({rle_max_retries})')
                print(f'RateLimitError: Sleeping for {delay} seconds')
                time.sleep(delay)
                delay *= expo_base
                print(f'Next error wait time is {delay} seconds. {rle_max_retries - rle_retries} RateLimitError retries remaining')
            except invalidreq as e:
                raise e
            except servererror as e:
                servererr_retries += 1
                if servererr_retries > servererr_max_retries:
                    print('Returning None for this request')
                    return None
                print('Encountered server error:', e)
                print(f'Sleeping for {delay} seconds')
                time.sleep(delay)
                delay *= expo_base
                print(f'Next error wait time is {delay} seconds. {rle_max_retries - rle_retries} server error retries remaining')
            except Exception as e:
                raise e
    return wrapper

@openai_error_handler
def model_get_embeddings(text_list):
	response = openai.Embedding.create(
		model=TEXT_EMBEDDINGS_MODEL,
		input=text_list,
	)
	time.sleep(WAITING_TIME)
	return pd.DataFrame([datum['embedding'] for datum in response['data']])
'''
Calls GPT-3 to generate a questions from the given context.
Currently, it will generate 3 questions.
'''

@openai_error_handler
def model_get_questions(context):
	response = openai.Completion.create(
		model=QA_GENERATING_MODEL,
		prompt=f'You are a financial analyst looking through some news about stocks and the market. Write one question based on the article below\nArticle: {context}\nQuestion:',
		presence_penalty=0.5,
		frequency_penalty=0.5,
		temperature=1,
		top_p=1,
		n=3,
		max_tokens=250,
	)
	time.sleep(WAITING_TIME)
	questions = [choice['text'][1:] for choice in response['choices']]
	# print(response['choices'])
	return pd.DataFrame(columns=[COL_CONTEXT, COL_QUESTION], data=[(context, question) for question in questions])

'''
Calls GPT-3 to answer the questions given the context.
'''


@openai_error_handler
def model_get_answers(context, questions):
	response = openai.Completion.create(
		model=QA_GENERATING_MODEL,
		prompt=f'You are a financial analyst looking through some news about stocks and the market. Write an answer to the question based on the article below\nQuestion: {questions}\nArticle: {context}\nAnswer:',
		presence_penalty=0.5,
		frequency_penalty=0.5,
		temperature=1,
		top_p=1,
		max_tokens=500,
	)
	time.sleep(WAITING_TIME)
	answers = response['choices'][0]['text'][1:]
	# print(response['choices'])
	return answers
