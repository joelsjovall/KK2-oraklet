import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

from app.chain.pipeline import build_ai_chain
from app.config import settings
from app.data import create_stats, get_columns, get_dtypes, has_dataset, read_csv_file, save_dataset
from app.schemas import AskRequest, AskResponse, PromptInput

app = FastAPI(title="KK2 Oraklet")
ai_chain = build_ai_chain()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/data/upload")
async def upload_data(file: UploadFile = File(...)):
    if file.filename is None or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file.")

    file_content = await file.read()

    try:
        dataframe = read_csv_file(file_content)
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty.")
    except Exception:
        raise HTTPException(status_code=400, detail="CSV file could not be read.")

    save_dataset(dataframe)

    return {
        "message": "Dataset uppladdat.",
        "rows": len(dataframe),
        "columns": list(dataframe.columns),
        "dtypes": {column: str(dtype) for column, dtype in dataframe.dtypes.items()},
    }


@app.get("/data/stats")
def get_stats():
    if not has_dataset():
        raise HTTPException(status_code=404, detail="No dataset has been uploaded.")

    return create_stats()


@app.post("/ai/ask", response_model=AskResponse)
def ask_ai(request: AskRequest) -> AskResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not has_dataset():
        raise HTTPException(status_code=400, detail="Upload a dataset before asking questions.")

    try:
        result = ai_chain.run(
            PromptInput(
                question=request.question,
                stats=create_stats(),
                columns=get_columns(),
                dtypes=get_dtypes(),
            )
        )
    except Exception as error:
        print(f"AI error: {error}")
        raise HTTPException(status_code=500, detail="AI could not create an answer.")

    return AskResponse(
        question=request.question,
        answer=result.answer,
        model=settings.model_name,
    )
