from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader
import io

router = APIRouter()


@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):

    # Check file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    try:
        # Read uploaded file
        file_bytes = await file.read()

        # Read PDF
        pdf = PdfReader(io.BytesIO(file_bytes))

        # Extract text
        extracted_text = ""

        for page in pdf.pages:
            text = page.extract_text()

            if text:
                extracted_text += text + "\n"

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the resume."
            )

        return {
            "message": "Resume uploaded successfully.",
            "filename": file.filename,
            "text": extracted_text
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Resume processing error:", error)

        raise HTTPException(
            status_code=500,
            detail="Failed to process resume."
        )