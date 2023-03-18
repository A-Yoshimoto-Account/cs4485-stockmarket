import os, pytest

import brains.openai_api.openai_controller as openai_api

def test_openai_api_disabled():
    openai_controller = openai_api.OpenAIController(os.getenv('OPENAI_API_KEY'), disable=True)
    response = openai_controller.access_model(
        endpoint=openai_api.CHATCOMPLETION,
        model='gpt-3.5-turbo',
        question="What's up?",
        context='yo',
        memory=[]
    )
    assert response == 'placeholder answer'

