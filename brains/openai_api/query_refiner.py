from brains.openai_api.openai_controller import COMPLETION
from brains.openai_api.openai_controller import OpenAIController

REFINE_TYPES = ['list']

# implement LlamaIndex list index for refining queries to OpenAI
# called by ModelController
class QueryRefiner:
    def query(
            openai_controller: OpenAIController,
            type: str,
            endpoint: str,
            model: str,
            question: str,
            context_list: list[str],
            memory: list[dict[str, str]],
            **kwargs
    ) -> str:
        if type not in REFINE_TYPES:
            raise Exception(f'{type} is not a supported refinement type')
        if type == 'list':
            if endpoint == COMPLETION:
                # Maybe use LlamaIndex ListIndex here?
                pass
            return QueryRefiner._list_query(
                openai_controller=openai_controller,
                endpoint=endpoint,
                model=model,
                question=question,
                context_list=context_list,
                memory=memory,
                **kwargs
            )

    def _list_query(
            openai_controller: OpenAIController,
            endpoint: str,
            model: str,
            question: str,
            context_list: list[str],
            memory: list[dict[str, str]],
            **kwargs
    ) -> str:
        first_context = context_list[0]
        context_answer = openai_controller.access_model(
            endpoint=endpoint,
            model=model,
            question=question,
            context=first_context,
            memory=memory
        )
        for new_context in context_list[1:]:
            follow_up_memory = [{
                'question': question,
                'answer': context_answer
            }]
            follow_up_question = 'Add to, edit, or change the answer with the new piece of context.'
            context_answer = openai_controller.access_model(
                endpoint=endpoint,
                model=model,
                question=follow_up_question,
                context=new_context,
                memory=follow_up_memory
            )

        return context_answer



    query = staticmethod(query)
    _list_query = staticmethod(_list_query)

