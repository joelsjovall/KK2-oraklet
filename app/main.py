import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

from app.data import create_stats, has_dataset, read_csv_file, save_dataset

app = FastAPI(title="KK2 Oraklet")

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
    }


@app.get("/data/stats")
def get_stats():
    if not has_dataset():
        raise HTTPException(status_code=404, detail="No dataset has been uploaded.")

    return create_stats()
