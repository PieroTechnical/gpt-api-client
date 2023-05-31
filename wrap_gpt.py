
import json
import openai


class ChatEnvironment:
    chat_history = ''
    ai_instances = []

    def __init__(self):
        self.ai_instances = []
        
    def user_ask_message(self, sender, message):
        if message: 
            self.send_message(sender, message)

        for instance in self.ai_instances:
            answer = instance.ask(self.chat_history)
            print(self.chat_history)
            self.send_message(self.ai_instances[0].name, answer)

    def send_message(self, sender, message):
        query = f'[{sender}]: {message}\n'
        self.chat_history = self.chat_history + query
        

class ApplicationManager:
    chat_environment = ChatEnvironment()

    @staticmethod
    def user_ask_message(sender, message):
        return __class__.chat_environment.user_ask_message(sender, message)

    @staticmethod
    def get_chat_history():
        return __class__.chat_environment.chat_history
    
    @staticmethod
    def ask_all():
        for instance in __class__.chat_environment.ai_instances:
            instance.ask(__class__.get_chat_history())

    @staticmethod
    def get_entity_personality_names():
        __class__.load_personality_archetypes_from_file('C:\\dev\\WrapGPT\\personality_archetypes.json')
        return list(__class__.entity_personality_archetypes.keys())
    
    @staticmethod
    def get_entity_personality_by_name(name):
        return __class__.entity_personality_archetypes[name]
    
    @staticmethod
    def get_list_models():
        models_json = openai.Model.list()
        id_values = [item['id'] for item in models_json['data']]
        return id_values
    
    @staticmethod
    def save_personality_archetypes_to_file(file_path):
        personalities_dict = {name: ApplicationManager.serialize_entity_personality(personality) 
                              for name, personality in ApplicationManager.entity_personality_archetypes.items()}
        with open(file_path, 'w') as file:
            json.dump(personalities_dict, file)

    @staticmethod
    def load_personality_archetypes_from_file(file_path):
        with open(file_path, 'r') as file:
            personalities_dict = json.load(file)

        ApplicationManager.entity_personality_archetypes = personalities_dict



class AIInstance:
    def __init__(self, entity_personality):
        self.name = entity_personality['name']
        self.prompt = entity_personality['prompt']
        self.engine = entity_personality['engine']

    def ask(self, input_prompt):
        prompt = f'''[{self.name}]: {self.prompt}\n{input_prompt}\n[{self.name}]:'''

        try:
            response = openai.Completion.create(
                engine=self.engine,
                prompt=prompt,
                max_tokens=150)
            
        except Exception as e:
            return str(e)
        
        return response.choices[0].text.strip() 

    def save_entity_personality(self):
        entity_personality = {
            'name' : self.name,
            'prompt' : self.prompt,
            'engine' : self.engine}
        
        return entity_personality

    def load_entity_personality(self, entity_personality):
        self.name = entity_personality['name']
        self.prompt = entity_personality['prompt']
        self.engine = entity_personality['engine']







'''

personality_dict = ApplicationManager.load_entity_personality_from_file('C:\\dev\\WrapGPT\\personality_archetypes.json')
self.ai_instances = [AIInstance(personality) for personality in personality_dict.values()]'''