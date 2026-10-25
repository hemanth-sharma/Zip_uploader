import os
import shutil
from pathlib import Path
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(title="Secure Blind Upload Server")

# Ensure the uploaded directory exists securely in the root
UPLOAD_DIR = Path("uploaded")
UPLOAD_DIR.mkdir(exist_ok=True)

# Authentication setup
# Best Practice: Set this via environment variable, e.g., export UPLOAD_API_KEY="your_secret"
API_KEY = os.getenv("UPLOAD_API_KEY")
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@app.get("/")
def read_root():
    """Health check endpoint. Reveals zero data or server structure."""
    return {"status": "online", "message": "Secure upload service active."}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    token: str = Security(verify_token)
):
    """
    Secure upload endpoint. Accepts any file type (including .zip), 
    sanitizes the filename, and stores it in the 'uploaded' directory.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    safe_filename = Path(file.filename).name
    
    unique_filename = f"{uuid.uuid4()}_{safe_filename}"
    file_path = UPLOAD_DIR / unique_filename

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    file_size = 0

    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    buffer.close()
                    if file_path.exists():
                        file_path.unlink()  # Delete the partial file
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File size exceeds the maximum limit of 50MB."
                    )
                buffer.write(chunk)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Could not process upload.")

    return {
        "message": "File uploaded successfully.",
        "stored_filename": unique_filename
    }