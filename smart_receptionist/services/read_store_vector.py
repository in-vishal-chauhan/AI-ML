import os
import glob
from docx import Document as DocxDocument
import fitz
import markdown
from logger import get_logger
from services.pinecone_service import PineconeService
from config import Config

logger = get_logger(__name__)

class ReadStoreVector:
    def __init__(self, documents_path="./documents/docx"):
        self.documents_path = documents_path

    def _read_txt(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _read_docx(self, path):
        doc = DocxDocument(path)
        return "\n".join(p.text for p in doc.paragraphs)

    def _read_pdf(self, path):
        doc = fitz.open(path)
        return "\n".join([page.get_text() for page in doc])

    def _read_md(self, path):
        with open(path, "r", encoding="utf-8") as f:
            raw_md = f.read()
            return markdown.markdown(raw_md)

    def query(self):
        file_readers = {
            ".txt": self._read_txt,
            ".docx": self._read_docx,
            ".pdf": self._read_pdf,
            ".md": self._read_md,
        }

        for ext, reader in file_readers.items():
            files = glob.glob(os.path.join(self.documents_path, f"**/*{ext}"), recursive=True)
            for file_path in files:
                try:
                    content = reader(file_path)

                    if not content.strip():
                        logger.error(f"Empty content in file: {file_path}")
                        continue

                    file_name = os.path.splitext(os.path.basename(file_path))[0]

                    record = [
                        {
                            "_id": file_name,
                            "chunk_text": content,
                        }
                    ]

                    return record
                except Exception as e:
                    logger.error(f"Failed to read file {file_path}: {e}")
                    continue