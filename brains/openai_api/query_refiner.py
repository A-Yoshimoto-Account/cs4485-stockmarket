from brains.openai_api.openai_controller import OpenAIController


# implement LlamaIndex list index for refining queries to OpenAI
# called by ModelController
class Refiner:
    def __init__(self, openai_controller: OpenAIController):
        self.openai = openai_controller

class ListRefiner(Refiner):
    def __init__(self, openai_controller: OpenAIController):
        super().__init__(openai_controller)

    def query(self, endpoint, model, question, context_list, memory):
        pass

