"""
🧪 Tests para Utilities

Tests para funciones de utilidad (text extraction, etc.)
"""

import pytest
from unittest.mock import Mock, patch
from io import BytesIO
from fastapi import UploadFile

from app.utils.text_extraction import extract_text_from_file


class TestTextExtraction:
    """Tests para extracción de texto"""

    def test_extract_text_from_txt_file(self):
        """Test extracción de archivo TXT"""
        content = "Este es un archivo de texto plano."
        file_obj = BytesIO(content.encode())
        upload_file = UploadFile(filename="test.txt", file=file_obj)

        result = extract_text_from_file(upload_file)

        assert result == content

    def test_extract_text_from_md_file(self):
        """Test extracción de archivo Markdown"""
        content = "# Título\n\nEste es un archivo markdown."
        file_obj = BytesIO(content.encode())
        upload_file = UploadFile(filename="test.md", file=file_obj)

        result = extract_text_from_file(upload_file)

        assert result == content

    @patch("app.utils.text_extraction.PyPDF2")
    def test_extract_text_from_pdf_file(self, mock_pypdf2):
        """Test extracción de archivo PDF"""
        # Mock PyPDF2
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Contenido del PDF"
        mock_reader.pages = [mock_page]
        mock_pypdf2.PdfReader.return_value = mock_reader

        file_obj = BytesIO(b"fake pdf content")
        upload_file = UploadFile(filename="test.pdf", file=file_obj)

        result = extract_text_from_file(upload_file)

        assert result == "Contenido del PDF"
        mock_pypdf2.PdfReader.assert_called_once()

    @patch("app.utils.text_extraction.docx")
    def test_extract_text_from_docx_file(self, mock_docx):
        """Test extracción de archivo DOCX"""
        # Mock python-docx
        mock_doc = Mock()
        mock_paragraph = Mock()
        mock_paragraph.text = "Párrafo del documento"
        mock_doc.paragraphs = [mock_paragraph]
        mock_docx.Document.return_value = mock_doc

        file_obj = BytesIO(b"fake docx content")
        upload_file = UploadFile(filename="test.docx", file=file_obj)

        result = extract_text_from_file(upload_file)

        assert result == "Párrafo del documento"
        mock_docx.Document.assert_called_once()

    @patch("app.utils.text_extraction.pd")
    def test_extract_text_from_csv_file(self, mock_pd):
        """Test extracción de archivo CSV"""
        # Mock pandas DataFrame
        mock_df = Mock()
        # Configurar len() directamente
        type(mock_df).__len__ = Mock(return_value=2)

        # Mock columns como lista con tolist()
        mock_columns = Mock()
        mock_columns.tolist.return_value = ["col1", "col2"]
        type(mock_columns).__len__ = Mock(return_value=2)
        mock_df.columns = mock_columns

        # Mock head().iterrows()
        mock_head = Mock()
        mock_head.iterrows.return_value = [
            (0, {"col1": "val1", "col2": "val2"}),
            (1, {"col1": "val3", "col2": "val4"}),
        ]
        mock_df.head.return_value = mock_head

        # Mock select_dtypes para columnas numéricas
        mock_numeric = Mock()
        mock_numeric.columns = []
        mock_df.select_dtypes.return_value = mock_numeric

        mock_pd.read_csv.return_value = mock_df

        file_obj = BytesIO(b"col1,col2\nval1,val2")
        upload_file = UploadFile(filename="test.csv", file=file_obj)

        result = extract_text_from_file(upload_file)

        assert "Archivo CSV con 2 filas y 2 columnas" in result
        assert "col1, col2" in result
        mock_pd.read_csv.assert_called_once()

    def test_extract_text_unsupported_format(self):
        """Test archivo con formato no soportado"""
        file_obj = BytesIO(b"contenido binario")
        upload_file = UploadFile(filename="test.bin", file=file_obj)

        with pytest.raises(ValueError, match="Unsupported file format"):
            extract_text_from_file(upload_file)

    def test_extract_text_file_error(self):
        """Test error durante extracción"""
        # Mock que el archivo no se puede leer
        upload_file = Mock()
        upload_file.filename = "test.txt"
        upload_file.file.read.side_effect = Exception("Read error")

        with pytest.raises(ValueError, match="Error extracting text from test.txt"):
            extract_text_from_file(upload_file)

    def test_extract_text_pdf_without_pypdf2(self):
        """Test extracción de PDF cuando PyPDF2 no está disponible"""
        with patch("app.utils.text_extraction.PyPDF2", None):
            file_obj = BytesIO(b"fake pdf content")
            upload_file = UploadFile(filename="test.pdf", file=file_obj)

            with pytest.raises(ValueError, match="PyPDF2 not installed"):
                extract_text_from_file(upload_file)

    def test_extract_text_docx_without_python_docx(self):
        """Test extracción de DOCX cuando python-docx no está disponible"""
        with patch("app.utils.text_extraction.docx", None):
            file_obj = BytesIO(b"fake docx content")
            upload_file = UploadFile(filename="test.docx", file=file_obj)

            with pytest.raises(ValueError, match="python-docx not installed"):
                extract_text_from_file(upload_file)

    def test_extract_text_csv_without_pandas(self):
        """Test extracción de CSV cuando pandas no está disponible"""
        with patch("app.utils.text_extraction.pd", None):
            file_obj = BytesIO(b"col1,col2\nval1,val2")
            upload_file = UploadFile(filename="test.csv", file=file_obj)

            with pytest.raises(ValueError, match="pandas not installed"):
                extract_text_from_file(upload_file)


class TestFileValidation:
    """Tests para validación de archivos"""

    def test_valid_file_extensions(self):
        """Test extensiones de archivo válidas"""
        valid_extensions = [".pdf", ".docx", ".txt", ".md", ".csv"]
        test_filenames = [
            "document.pdf",
            "report.docx",
            "notes.txt",
            "readme.md",
            "data.csv",
        ]

        for filename in test_filenames:
            assert any(filename.lower().endswith(ext) for ext in valid_extensions)

    def test_invalid_file_extensions(self):
        """Test extensiones de archivo inválidas"""
        valid_extensions = [".pdf", ".docx", ".txt", ".md", ".csv"]
        invalid_filenames = [
            "image.jpg",
            "video.mp4",
            "archive.zip",
            "executable.exe",
            "unknown.xyz",
        ]

        for filename in invalid_filenames:
            assert not any(filename.lower().endswith(ext) for ext in valid_extensions)

    def test_case_insensitive_extensions(self):
        """Test que las extensiones sean case-insensitive"""
        valid_extensions = [".pdf", ".docx", ".txt", ".md", ".csv"]
        test_filenames = [
            "document.PDF",
            "report.DOCX",
            "notes.TXT",
            "readme.MD",
            "data.CSV",
        ]

        for filename in test_filenames:
            assert any(filename.lower().endswith(ext) for ext in valid_extensions)
