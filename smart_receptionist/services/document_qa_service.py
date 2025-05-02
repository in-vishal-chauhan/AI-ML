import os
import glob
from docx import Document as DocxDocument
import fitz
import markdown
from logger import get_logger
logger = get_logger(__name__)

class DocumentQAService:
    def __init__(self, documents_path="./documents"):
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

    def _load_documents(self):
        texts = []

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
                    texts.append(reader(file_path))
                except Exception as e:
                    logger.error(f"Failed to read {file_path}: {e}")
                    continue

        return texts

    def query(self, user_input, groq_api):
        texts = self._load_documents()
        context = "\n\n".join(texts)

        prompt = f"""
        Use the following context to answer the question.

        --- Context ---
        {context}
        ----------------

        Question: {user_input}
        """

        return groq_api.ask(prompt.strip(), user_input)
