CHAT_SYSTEM = 'You are a '

COMPLETION_PROMPT = ''
COMPLETION_STOP = ''

class OpenAIPromptCreator:
    def __init__(self, **kwargs):
        self.system = None if 'system' not in kwargs else kwargs['system']
        self.prompt_prefix = None if 'prompt_prefix' not in kwargs else kwargs['prompt_prefix']
        self.prompt_suffix = None if 'prompt_suffix' not in kwargs else kwargs['prompt_suffix']
        self.completion_stopping = None if 'completion_stopping' not in kwargs else kwargs['completion_stopping']

    def create_chat_messages(self, question: str, context: str, memory: dict) ->  list[dict]:
        messages = []
        messages.append({
            'role': 'system',
            'content': self.system
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

    def create_completion_prompt(self, question, context):
        prompt = f'{self.prompt_prefix}{question}\n\n{context}{self.prompt_suffix}'
        return prompt

