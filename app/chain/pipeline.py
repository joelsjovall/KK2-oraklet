from app.chain.runnable import Runnable
from app.chain.steps import LLMRunner, PromptBuilder, ResponseParser
from app.schemas import ParserOutput, PromptInput


def build_ai_chain() -> Runnable[PromptInput, ParserOutput]:
    prompt_builder = PromptBuilder()
    llm_runner = LLMRunner()
    response_parser = ResponseParser()

    return prompt_builder | llm_runner | response_parser
