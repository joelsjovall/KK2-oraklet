from pydantic import BaseModel

from app.chain.runnable import Runnable


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
