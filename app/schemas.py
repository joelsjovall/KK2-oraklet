from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str


class PromptInput(BaseModel):
    question: str
    stats: dict
    columns: list[str]
    dtypes: dict[str, str]
    preview_records: list[dict]


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
