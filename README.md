# KK2 Oraklet

KK2 Oraklet är en FastAPI-applikation för att ladda upp ett CSV-dataset, analysera det med Pandas och ställa frågor om datat med en liten språkmodell från HuggingFace.

Projektet använder:

- FastAPI för REST-API
- Pandas för CSV-läsning och statistik
- Transformers för SmolLM2
- En egen typad Runnable-kedja med `|`-operatorn
- Pytest för tester

## Installation

Projektet använder `uv`.

Installera beroenden:

```bash
uv sync
```

## Starta servern

Kör:

```bash
uv run uvicorn app.main:app --reload
```

Öppna sedan Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### GET /health

Kontrollerar att API:t kör.

Exempel:

```bash
curl http://127.0.0.1:8000/health
```

Svar:

```json
{
  "status": "ok"
}
```

### POST /data/upload

Laddar upp en CSV-fil via form-data. Filen måste sluta på `.csv`.

Exempeldata:

```csv
name,age
Alice,10
Bob,20
Charlie,30
```

Exempelsvar:

```json
{
  "message": "Dataset uppladdat.",
  "rows": 3,
  "columns": ["name", "age"],
  "dtypes": {
    "name": "str",
    "age": "int64"
  }
}
```

Datasetet sparas temporärt i minnet. Om servern startas om behöver filen laddas upp igen.

### GET /data/stats

Returnerar statistik från `df.describe()` som JSON.

Om inget dataset har laddats upp returneras `404`.

Exempel:

```bash
curl http://127.0.0.1:8000/data/stats
```

### POST /ai/ask

Tar emot en fråga om det uppladdade datasetet och returnerar ett svar från SmolLM2.

Exempel:

```json
{
  "question": "Who has the highest age?"
}
```

Exempelsvar:

```json
{
  "question": "Who has the highest age?",
  "answer": "Charlie has the highest age.",
  "model": "HuggingFaceTB/SmolLM2-135M-Instruct"
}
```

För att använda `/ai/ask` måste ett dataset först laddas upp med `/data/upload`.

## AI-kedjan

AI-flödet byggs med en egen Runnable-kedja:

```python
prompt_builder | llm_runner | response_parser
```

Kedjan består av tre steg:

- `PromptBuilder` bygger en prompt med fråga, kolumner, datatyper, exempelrader och Pandas-statistik.
- `LLMRunner` anropar SmolLM2 via `transformers.pipeline`.
- `ResponseParser` städar modellens råa text till ett strukturerat svar.

Varje steg använder Pydantic-modeller för input och output.

Modellen som används är:

```text
HuggingFaceTB/SmolLM2-135M-Instruct
```

Första gången modellen används laddas den ner till HuggingFace-cachen lokalt.

## Tester

Kör testerna med:

```bash
uv run pytest app/tests/ -v
```

Testerna täcker:

- Runnable-kedjan och `|`-operatorn
- separata kedjesteg
- uppladdning av CSV
- statistik-endpoint
- AI-endpoint med mockad kedja
- felhantering för saknat dataset och ogiltig fil

## Projektstruktur

```text
app/
  main.py
  data.py
  schemas.py
  config.py
  chain/
    runnable.py
    steps.py
    pipeline.py
  tests/
    test_endpoints.py
    test_chain.py
```

## Antaganden

- Dataset sparas bara i minnet.
- Endast CSV-filer accepteras.
- SmolLM2 körs lokalt via `transformers.pipeline`.
- Modellen är liten och kan ibland ge felaktiga eller hallucinerade svar.
- `.env` används inte just nu, men finns med i `.gitignore` om API-nycklar skulle behövas senare.
