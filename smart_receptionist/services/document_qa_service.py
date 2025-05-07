import os
import glob
from docx import Document as DocxDocument
import fitz
import markdown
from logger import get_logger
import json

logger = get_logger(__name__)

class DocumentQAService:
    def __init__(self, documents_path="./documents", chunk_size=2000):
        self.documents_path = documents_path
        self.chunk_size = chunk_size

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

    def _chunk_text(self, text):
        """Chunk large text into smaller parts."""
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start:start + self.chunk_size])
            start += self.chunk_size
        return chunks

    def query(self, user_input, groq_api):
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
                    
                    # If the content is too large, break it into chunks
                    chunks = self._chunk_text(content) if len(content) > self.chunk_size else [content]
                    
                    for chunk in chunks:
                        prompt = f"""
                        Use the following context to answer the question.
                        If you find the answer, respond in **valid JSON format** like this:
                        {{
                            "match": "yes",
                            "answer": "Your detailed answer here."
                        }}
                        If not found, use:
                        {{
                            "match": "no",
                            "answer": "Sorry, I couldn't find the answer."
                        }}

                        --- Context ---
                        {chunk}
                        ----------------

                        Question: {user_input}
                        """

                        response = groq_api.ask(prompt.strip(), user_input)
                        if response:
                            try:
                                response_dict = json.loads(response)
                                if response_dict.get("match") == "yes" and "answer" in response_dict:
                                    return response_dict["answer"]
                                else:
                                    continue
                            except json.JSONDecodeError as e:
                                logger.error(f"Invalid JSON response from AI for file {file_path}: {e}")
                                continue
                except Exception as e:
                    logger.error(f"Failed to read file {file_path}: {e}")
                    continue