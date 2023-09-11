from langchain.chat_models import ChatOpenAI
from langchain.llms import ChatGLM 
from langchain.chains import LLMChain

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from utils import LOG

def createLLM(model_name: str = "gpt-3.5-turbo", verbose: bool = True):
    if model_name == 'chatglm6b' :
        chat = ChatGLM(endpoint_url='http://127.0.0.1:8000',
                        max_token=80000,
                        history=[],
                        top_p=0.9,
                        model_kwargs={"sample_model_args": False }, verbose=verbose)
    else: 
        chat = ChatOpenAI(model_name=model_name, temperature=0, verbose=verbose)
    
    return chat

class TranslationChain:
    def __init__(self, model_name: str = "gpt-3.5-turbo", verbose: bool = True):
        
        # 翻译任务指令始终由 System 角色承担
        template = (
            """You are a translation expert, proficient in various languages. You're good at language style of {style_name}.\n
            Translates {source_language} to {target_language}."""
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        # 待翻译文本由 Human 角色输入
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        # 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        # 为了翻译结果的稳定性，将 temperature 设置为 0
        chat = createLLM(model_name, verbose)

        self.chain = LLMChain(llm=chat, prompt=chat_prompt_template, verbose=verbose)

    def run(self, text: str, source_language: str, target_language: str, translation_style: str = "CNN Writer") -> (str, bool):
        result = ""
        try:
            result = self.chain.run({
                "text": text,
                "style_name": translation_style,
                "source_language": source_language,
                "target_language": target_language,
            })
        except Exception as e:
            LOG.error(f"An error occurred during translation: {e}")
            return result, False

        return result, True