from abc import ABC, abstractmethod
from typing import Generic, TypeVar


InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")
NextOutputType = TypeVar("NextOutputType")


class Runnable(ABC, Generic[InputType, OutputType]):
    @abstractmethod
    def run(self, data: InputType) -> OutputType:
        pass

    def __or__(
        self,
        next_step: "Runnable[OutputType, NextOutputType]",
    ) -> "Runnable[InputType, NextOutputType]":
        return RunnableSequence(self, next_step)


class RunnableSequence(Runnable[InputType, OutputType]):
    def __init__(self, first: Runnable, second: Runnable) -> None:
        self.first = first
        self.second = second

    def run(self, data: InputType) -> OutputType:
        first_result = self.first.run(data)
        return self.second.run(first_result)
