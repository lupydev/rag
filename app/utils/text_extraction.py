import io
from fastapi import UploadFile
import PyPDF2
import docx
import pandas as pd


def extract_text_from_file(file: UploadFile) -> str:
    """
    Extrae texto de diferentes tipos de archivo

    Args:
        file: Archivo subido

    Returns:
        Texto extraído

    Raises:
        ValueError: Si el formato no es soportado
    """
    filename = file.filename.lower()

    try:
        if filename.endswith(".pdf"):
            return extract_text_from_pdf(file)
        elif filename.endswith(".docx"):
            return extract_text_from_docx(file)
        elif filename.endswith(".txt") or filename.endswith(".md"):
            return extract_text_from_txt(file)
        elif filename.endswith(".csv"):
            return extract_text_from_csv(file)
        else:
            raise ValueError(f"Unsupported file format: {filename}")

    except Exception as e:
        raise ValueError(f"Error extracting text from {filename}: {str(e)}")


def extract_text_from_pdf(file: UploadFile) -> str:
    """Extrae texto de PDF"""
    if PyPDF2 is None:
        raise ValueError("PyPDF2 not installed. Run: pip install PyPDF2")

    content = file.file.read()
    pdf_file = io.BytesIO(content)

    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""

    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"

    file.file.seek(0)  # Reset file pointer
    return text.strip()


def extract_text_from_docx(file: UploadFile) -> str:
    """Extrae texto de DOCX"""
    if docx is None:
        raise ValueError("python-docx not installed. Run: pip install python-docx")

    content = file.file.read()
    doc_file = io.BytesIO(content)

    doc = docx.Document(doc_file)
    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    file.file.seek(0)  # Reset file pointer
    return text.strip()


def extract_text_from_txt(file: UploadFile) -> str:
    """Extrae texto de archivo de texto plano"""
    content = file.file.read()

    # Intentar diferentes encodings
    encodings = ["utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            text = content.decode(encoding)
            file.file.seek(0)  # Reset file pointer
            return text.strip()
        except UnicodeDecodeError:
            continue

    raise ValueError("Could not decode text file with any supported encoding")


def extract_text_from_csv(file: UploadFile) -> str:
    """Extrae texto de CSV convirtiéndolo a texto"""
    if pd is None:
        raise ValueError("pandas not installed. Run: pip install pandas")

    content = file.file.read()
    csv_file = io.StringIO(content.decode("utf-8"))

    df = pd.read_csv(csv_file)  # Convertir DataFrame a texto descriptivo
    text_parts = []

    # Headers
    text_parts.append(f"Archivo CSV con {len(df)} filas y {len(df.columns)} columnas.")
    text_parts.append(f"Columnas: {', '.join(df.columns.tolist())}")

    # Sample data (primeras 5 filas)
    text_parts.append("\nDatos de muestra:")
    for idx, row in df.head().iterrows():
        row_text = ", ".join([f"{col}: {val}" for col, val in row.items()])
        text_parts.append(f"Fila {idx + 1}: {row_text}")

    # Summary stats for numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns
    if len(numeric_cols) > 0:
        text_parts.append("\nEstadísticas de columnas numéricas:")
        for col in numeric_cols:
            mean_val = df[col].mean()
            text_parts.append(f"{col}: promedio {mean_val:.2f}")

    file.file.seek(0)  # Reset file pointer
    return "\n".join(text_parts)
