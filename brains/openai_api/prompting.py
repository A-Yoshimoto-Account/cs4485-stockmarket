CHAT_SYSTEM = 'You are a '

COMPLETION_PROMPT = ''
COMPLETION_STOP = ''

class OpenAIPromptCreator:
    def __init__(self):
        pass

    def create_chat_messages(self, question, context, memory):
        messages = []
        messages.append({
            'role': 'system',
            'content': CHAT_SYSTEM
        })
        for interaction in memory:
            messages.append({
                'role': 'user',
                'content': interaction['question']
            })
            messages.append({
                'role': 'assistant',
                'content': interaction['question']
            })
        messages.append({
            'role': 'assistant',
            'content': context
        })
        messages.append({
            'role': 'user',
            'content': question
        })
        return messages