from collections.abc import Callable
from typing import Any

from app.chain.runnable import Runnable
from app.config import settings
from app.schemas import LLMInput, ParserInput, ParserOutput, PromptInput


class PromptBuilder(Runnable[PromptInput, LLMInput]):
    def run(self, data: PromptInput) -> LLMInput:
        prompt = (
            "Du är KK2 Oraklet, en hjälpsam AI-assistent för en skoluppgift.\n"
            "Svara kort och tydligt på svenska.\n\n"
            f"Fråga: {data.question}\n"
            "Svar:"
        )
        return LLMInput(prompt=prompt)


class LLMRunner(Runnable[LLMInput, ParserInput]):
    def __init__(
        self,
        generator: Callable[[str], Any] | None = None,
        model_name: str = settings.model_name,
        max_new_tokens: int = settings.max_new_tokens,
    ) -> None:
        self.generator = generator
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens

    def run(self, data: LLMInput) -> ParserInput:
        generator = self._get_generator()
        result = generator(data.prompt)
        generated_text = self._extract_text(result)
        return ParserInput(generated_text=generated_text)

    def _get_generator(self) -> Callable[[str], Any]:
        if self.generator is None:
            from transformers import pipeline

            self.generator = pipeline(
                "text-generation",
                model=self.model_name,
                max_new_tokens=self.max_new_tokens,
            )

        return self.generator

    def _extract_text(self, result: Any) -> str:
        if isinstance(result, str):
            return result

        if isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            if isinstance(first_result, dict):
                generated_text = first_result.get("generated_text", "")
                return str(generated_text)

        return str(result)


class ResponseParser(Runnable[ParserInput, ParserOutput]):
    def run(self, data: ParserInput) -> ParserOutput:
        answer = data.generated_text

        if "Svar:" in answer:
            answer = answer.split("Svar:")[-1]

        answer = answer.strip()

        if not answer:
            answer = "Jag kunde inte skapa ett svar."

        return ParserOutput(answer=answer)
