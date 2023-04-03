import os, pytest, dotenv
import brains.openai_api.openai_controller as openai_api

dotenv.load_dotenv()

def test_openai_api_disabled():
    openai_controller = openai_api.OpenAIController(os.getenv('OPENAI_API_KEY'), disable_embeds=True, disable_completions=True)
    response = openai_controller.access_model(
        endpoint=openai_api.CHATCOMPLETION,
        model='gpt-3.5-turbo',
        question="What's up?",
        context='yo',
        memory=[]
    )
    assert response == 'placeholder answer'

def test_openai_multiple_embeds():
    openai_controller = openai_api.OpenAIController(os.getenv('OPENAI_API_KEY'), disable_completions=True, disable_embeds=False)
    response = openai_controller.access_model(
        endpoint=openai_api.EMBEDDING,
        model=openai_api.EMBEDDING_MODELS[0],
        text=['hello', 'what\'s up', 'what is your name?'],
    )
    print(response)
    assert len(response) == 3