from fastapi import HTTPException, UploadFile, status
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO


def extract_text_buffer(file: UploadFile):
    file_ext = file.filename.split(".")[-1].lower()
    contents = BytesIO(file.file.read())

    if file_ext == "pdf":
        reader = PdfReader(contents)
        return "\n".join(
            page.extract_text() for page in reader.pages if page.extract_text()
        )
    elif file_ext == "docx":
        doc = Document(contents)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file_ext in ["txt", "md"]:
        contents.seek(0)
        return contents.read().decode("utf-8")
    elif file_ext == "csv":
        contents.seek(0)
        return contents.read().decode("utf-8")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )
