
import contextlib
import io
import json
import os
import sys
import traceback
import openai

MAX_TOKENS = 300

class ChatEnvironment:
    chat_history = ''
    ai_instances = []

    def __init__(self, ai_instances = []):
        self.ai_instances = ai_instances
        
    def user_ask_message(self, sender, message):
        output = ''

        if message: 
            self.send_message(sender, message)

        for instance in self.ai_instances:
            output = instance.ask(self.chat_history)
            self.send_message(instance.name, output)

        return output

    def send_message(self, sender, message):
        query = f'[{sender}]: {message}\n'
        self.chat_history = self.chat_history + query
        

class ApplicationManager:
    script_output = ''
    chat_environment = ChatEnvironment()
    ui = ''

    @staticmethod
    def user_ask_message(sender, message):
        result = __class__.chat_environment.user_ask_message(sender, message)
        __class__.extract_python_code_to_new_tab(result)
        return result

    @staticmethod
    def get_chat_history():
        return __class__.chat_environment.chat_history
    
    @staticmethod
    def ask_all():
        for instance in __class__.chat_environment.ai_instances:
            instance.ask(__class__.get_chat_history())

    @staticmethod
    def get_entity_personality_names():
        __class__.load_personality_archetypes_from_file(__class__.get_personality_file())
        return list(__class__.entity_personality_archetypes.keys())

    @staticmethod
    def get_personality_file():
        current_module_path = os.path.abspath(__file__)
        current_module_directory = os.path.dirname(current_module_path)

        return f'{current_module_directory}\\personality_archetypes.json'
    
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
        personalities_dict = {name: __class__.serialize_entity_personality(personality) 
                              for name, personality in __class__.entity_personality_archetypes.items()}
        with open(file_path, 'w') as file:
            json.dump(personalities_dict, file)

    @staticmethod
    def load_personality_archetypes_from_file(file_path):
        with open(file_path, 'r') as file:
            personalities_dict = json.load(file)

        __class__.entity_personality_archetypes = personalities_dict

    @staticmethod
    def extract_python_code_to_new_tab(message):
        if '```python' in message:
            code_snippets = message.split('```python')[1:]
            code_snippets = [snippet.split('```')[0] for snippet in code_snippets]

            entire_code = "\n".join(code_snippets)

            __class__.ui.add_script_tab(entire_code, True)
    
    @staticmethod
    def execute(code, auto=False):
        try:
            message = ApplicationManager.exec_with_buffer(code)
        except Exception as e:
            exc_info = sys.exc_info()
            traceback_message = traceback.format_exception(*exc_info)
            message = "ERROR: " + str(e) + "\n" + "".join(traceback_message)

            if auto:
                message += ApplicationManager.ask_auto_debugger(__class__, code, message)
        
        ApplicationManager.script_output += message + '\n'
        return message

    @staticmethod
    def ask_auto_debugger(__class__, code, message):
        print(f"Asking auto debugger {message}")
        __class__.auto_debugger = AIInstance(__class__.get_entity_personality_by_name("auto_debugger"))
        debug_response = __class__.auto_debugger.ask(f'\nCODE:\n{code}\n{message}')
        __class__.extract_python_code_to_new_tab(debug_response)
        return f'\n[auto_debug]: {debug_response}'

    @staticmethod
    def exec_with_buffer(code):
        # Create a string buffer and a context manager for temporary redirection
        buffer = io.StringIO()
        namespace = {}  # Dictionary to serve as local namespace
        with contextlib.redirect_stdout(buffer):
            exec(code, globals(), namespace)
            # Append the result of the last expression to buffer if it's not None
        if namespace.get('_'):  # '_' is traditionally used for the last expression result
            buffer.write(str(namespace['_']))
        return buffer.getvalue()
    
    
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
                max_tokens=MAX_TOKENS)
            
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

