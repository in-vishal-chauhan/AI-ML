import os
import glob
from docx import Document as DocxDocument
from logger import get_logger
import re

logger = get_logger(__name__)

class ReadStoreVector:
    def __init__(self, documents_path="./documents/docx", chunk_size=50):
        self.documents_path = documents_path
        self.chunk_size = chunk_size

    def _read_docx(self, path):
        doc = DocxDocument(path)
        return "\n".join(p.text for p in doc.paragraphs)

    def _chunk_text(self, text):
        tokens = re.findall(r'\S+', text)
        total_words = len(tokens)
        chunks = []

        for i in range(0, total_words, self.chunk_size):
            chunk = tokens[i:i + self.chunk_size]
            chunks.append(" ".join(chunk))

        return chunks

    def query(self):
        file_readers = {
            ".docx": self._read_docx,
        }

        all_chunks = []

        for ext, reader in file_readers.items():
            files = glob.glob(os.path.join(self.documents_path, f"**/*{ext}"), recursive=True)
            for file_path in files:
                try:
                    content = reader(file_path)

                    if not content.strip():
                        logger.error(f"Empty content in file: {file_path}")
                        continue

                    chunks = self._chunk_text(content)

                    for idx, chunk in enumerate(chunks):
                        file_name = os.path.splitext(os.path.basename(file_path))[0]
                        record = {"_id": f"{file_name}_chunk_{idx + 1}", "chunk_text": chunk}
                        all_chunks.append(record)

                except Exception as e:
                    logger.error(f"Failed to read file {file_path}: {e}")
                    continue
        return all_chunks