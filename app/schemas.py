from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


class PromptInput(BaseModel):
    question: str


class PromptOutput(BaseModel):
    prompt: str


class LLMInput(BaseModel):
    prompt: str


class LLMOutput(BaseModel):
    generated_text: str


class ParserInput(BaseModel):
    generated_text: str


class ParserOutput(BaseModel):
    answer: str
