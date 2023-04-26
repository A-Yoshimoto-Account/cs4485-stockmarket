import random

from brains.openai_api.openai_controller import COMPLETION
from brains.openai_api.openai_controller import OpenAIController

REFINE_TYPES = ['list']


# implement LlamaIndex list index for refining queries to OpenAI
# called by ModelController
class QueryRefiner:
    """_summary_ Refine a query to OpenAI.
    Args:
        openai_controller (OpenAIController): The instance of the OpenAIController class.
        type (str): The type of refinement to use.
        endpoint (str): The OpenAI endpoint to use for answering.
        model (str): The OpenAI model to use for answering.
        question (str): The question to ask the model.
        context_list (list[str]): The list of contexts to use for refinement.
        memory (list[dict[str, str]]): The previous questions to use as context.
        kwargs (dict): Additional arguments to pass to the refinement function.
        
    Returns:
        QueryRefiner._list_query().
    """
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
    """
    _summary_ Refine a query to OpenAI using a list of contexts, one at a time (in random order).
    Args:
        opoenai_controller (OpenAIController): The instance of the OpenAIController class.
        endpoint (str): The OpenAI endpoint to use for answering.
        model (str): The OpenAI model to use for answering.
        question (str): The question to ask the model.
        context_list (list[str]): The list of contexts to use for refinement.
        memory (list[dict[str, str]]): The previous questions to use as context.
        kwargs (dict): Additional arguments to pass to the refinement function.
        
    Returns:
        context_answer (str): The response contextualized from the model.
    """
    def _list_query(
            openai_controller: OpenAIController,
            endpoint: str,
            model: str,
            question: str,
            context_list: list[str],
            memory: list[dict[str, str]],
            **kwargs
    ) -> str:
        random.shuffle(context_list)
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

