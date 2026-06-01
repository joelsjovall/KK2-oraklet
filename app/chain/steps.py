import json
from collections.abc import Callable
from typing import Any

from app.chain.runnable import Runnable
from app.config import settings
from app.schemas import LLMInput, ParserInput, ParserOutput, PromptInput


class PromptBuilder(Runnable[PromptInput, LLMInput]):
    name: str = "prompt_builder"

    def invoke(self, data: PromptInput) -> LLMInput:
        stats_json = json.dumps(data.stats, ensure_ascii=False)
        records_json = json.dumps(data.preview_records, ensure_ascii=False)

        prompt = (
            "Answer the user's question about the CSV dataset.\n"
            "Use only the dataset information below. Answer with one short sentence.\n"
            "Write only the answer, no labels and no repeated text.\n\n"
            f"Columns: {data.columns}\n"
            f"Data types: {data.dtypes}\n"
            f"Dataset rows preview: {records_json}\n"
            f"Statistics from pandas describe(): {stats_json}\n\n"
            f"Question: {data.question}\n"
            "Answer:"
        )
        return LLMInput(prompt=prompt)


class LLMRunner(Runnable[LLMInput, ParserInput]):
    name: str = "llm_runner"
    generator: Callable[[str], Any] | None = None
    model_name: str = settings.model_name
    max_new_tokens: int = settings.max_new_tokens

    def invoke(self, data: LLMInput) -> ParserInput:
        generator = self._get_generator()
        result = generator(
            data.prompt,
            max_new_tokens=self.max_new_tokens,
            return_full_text=False,
            do_sample=False,
            repetition_penalty=1.2,
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
    name: str = "response_parser"

    def invoke(self, data: ParserInput) -> ParserOutput:
        answer = data.generated_text
        answer = answer.replace("\\n", "\n")
        answer = answer.replace('\\"', '"')

        for marker in ["Svar:", "Answer in Swedish:", "Answer:", "Question:"]:
            if marker in answer:
                answer = answer.split(marker, 1)[1]
                break

        answer = answer.strip()
        answer = answer.strip(" \"'")

        labels = ("Svar:", "Answer in Swedish:", "Answer:", "Question:")
        lines = [
            line.strip(" \"'")
            for line in answer.splitlines()
            if line.strip() and not line.strip().startswith(labels)
        ]
        if lines:
            answer = lines[0]

        if not answer:
            answer = "Jag kunde inte skapa ett svar."

        return ParserOutput(answer=answer)
