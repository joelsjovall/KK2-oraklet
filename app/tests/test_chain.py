from pydantic import BaseModel

from app.chain.runnable import Runnable
from app.chain.steps import LLMRunner, PromptBuilder, ResponseParser
from app.schemas import LLMInput, ParserInput, ParserOutput, PromptInput


class NumberInput(BaseModel):
    value: int


class NumberOutput(BaseModel):
    value: int


class DoubleNumber(Runnable[NumberInput, NumberOutput]):
    def invoke(self, data: NumberInput) -> NumberOutput:
        return NumberOutput(value=data.value * 2)


class AddThree(Runnable[NumberOutput, NumberOutput]):
    def invoke(self, data: NumberOutput) -> NumberOutput:
        return NumberOutput(value=data.value + 3)


def test_runnable_can_be_chained_with_pipe_operator() -> None:
    chain = DoubleNumber() | AddThree()

    result = chain.invoke(NumberInput(value=5))

    assert result == NumberOutput(value=13)


def test_prompt_builder_creates_prompt_from_question_and_stats() -> None:
    result = PromptBuilder().invoke(
        PromptInput(
            question="Vad ar medelvardet?",
            stats={"score": {"mean": 15.0}},
            columns=["name", "score"],
            dtypes={"name": "object", "score": "int64"},
            preview_records=[{"name": "Alice", "score": 10}],
        )
    )

    assert isinstance(result, LLMInput)
    assert "Vad ar medelvardet?" in result.prompt
    assert "score" in result.prompt
    assert "Alice" in result.prompt
    assert "15.0" in result.prompt
    assert "Answer:" in result.prompt


def test_llm_runner_uses_given_generator() -> None:
    def fake_generator(prompt: str, **kwargs) -> list[dict[str, str]]:
        return [{"generated_text": prompt + " Ett test-svar."}]

    result = LLMRunner(generator=fake_generator).invoke(LLMInput(prompt="Answer:"))

    assert isinstance(result, ParserInput)
    assert "Ett test-svar." in result.generated_text


def test_response_parser_returns_clean_answer() -> None:
    result = ResponseParser().invoke(ParserInput(generated_text="Question: Hej\nAnswer: Hej tillbaka"))

    assert result == ParserOutput(answer="Hej tillbaka")


def test_response_parser_removes_repeated_labels() -> None:
    result = ResponseParser().invoke(
        ParserInput(
            generated_text='"Oraklet"\\n\\nAnswer:\\nCharlie ar aldst.\\nAnswer:'
        )
    )

    assert result == ParserOutput(answer="Charlie ar aldst.")


def test_full_ai_chain_with_fake_llm() -> None:
    def fake_generator(prompt: str, **kwargs) -> list[dict[str, str]]:
        return [{"generated_text": prompt + " Detta ar ett kedjesvar."}]

    chain = PromptBuilder() | LLMRunner(generator=fake_generator) | ResponseParser()

    result = chain.invoke(
        PromptInput(
            question="Fungerar kedjan?",
            stats={"score": {"mean": 15.0}},
            columns=["score"],
            dtypes={"score": "int64"},
            preview_records=[{"score": 10}],
        )
    )

    assert result == ParserOutput(answer="Detta ar ett kedjesvar.")
