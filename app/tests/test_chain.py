from pydantic import BaseModel

from app.chain.runnable import Runnable
from app.chain.steps import LLMRunner, PromptBuilder, ResponseParser
from app.schemas import LLMInput, ParserInput, ParserOutput, PromptInput


class NumberInput(BaseModel):
    value: int


class NumberOutput(BaseModel):
    value: int


class DoubleNumber(Runnable[NumberInput, NumberOutput]):
    def run(self, data: NumberInput) -> NumberOutput:
        return NumberOutput(value=data.value * 2)


class AddThree(Runnable[NumberOutput, NumberOutput]):
    def run(self, data: NumberOutput) -> NumberOutput:
        return NumberOutput(value=data.value + 3)


def test_runnable_can_be_chained_with_pipe_operator() -> None:
    chain = DoubleNumber() | AddThree()

    result = chain.run(NumberInput(value=5))

    assert result == NumberOutput(value=13)


def test_prompt_builder_creates_prompt_from_question() -> None:
    result = PromptBuilder().run(PromptInput(question="Vad är medelvärde?"))

    assert isinstance(result, LLMInput)
    assert "Vad är medelvärde?" in result.prompt
    assert "Svar:" in result.prompt


def test_llm_runner_uses_given_generator() -> None:
    def fake_generator(prompt: str) -> list[dict[str, str]]:
        return [{"generated_text": prompt + " Ett test-svar."}]

    result = LLMRunner(generator=fake_generator).run(LLMInput(prompt="Svar:"))

    assert isinstance(result, ParserInput)
    assert "Ett test-svar." in result.generated_text


def test_response_parser_returns_clean_answer() -> None:
    result = ResponseParser().run(ParserInput(generated_text="Fråga: Hej\nSvar: Hej tillbaka"))

    assert result == ParserOutput(answer="Hej tillbaka")


def test_full_ai_chain_with_fake_llm() -> None:
    def fake_generator(prompt: str) -> list[dict[str, str]]:
        return [{"generated_text": prompt + " Detta är ett kedjesvar."}]

    chain = PromptBuilder() | LLMRunner(generator=fake_generator) | ResponseParser()

    result = chain.run(PromptInput(question="Fungerar kedjan?"))

    assert result == ParserOutput(answer="Detta är ett kedjesvar.")
