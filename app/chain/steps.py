import json
from collections.abc import Callable
from typing import Any

from app.chain.runnable import Runnable
from app.config import settings
from app.schemas import LLMInput, ParserInput, ParserOutput, PromptInput


class PromptBuilder(Runnable[PromptInput, LLMInput]):
    def run(self, data: PromptInput) -> LLMInput:
        stats_json = json.dumps(data.stats, ensure_ascii=False)

        prompt = (
            "You are KK2 Oraklet, an assistant that answers questions about a CSV dataset.\n"
            "Answer briefly in Swedish. Use only the dataset information below.\n\n"
            f"Columns: {data.columns}\n"
            f"Data types: {data.dtypes}\n"
            f"Statistics from pandas describe(): {stats_json}\n\n"
            f"Question: {data.question}\n"
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
        result = generator(
            data.prompt,
            max_new_tokens=self.max_new_tokens,
            return_full_text=False,
        )
        generated_text = self._extract_text(result)
        return ParserInput(generated_text=generated_text)

    def _get_generator(self) -> Callable[[str], Any]:
        if self.generator is None:
            from transformers import pipeline

            self.generator = pipeline(
                "text-generation",
                model=self.model_name,
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
