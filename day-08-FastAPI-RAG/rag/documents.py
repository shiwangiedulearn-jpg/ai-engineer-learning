from pathlib import Path
import fitz
from docx import Document

def extract_text(file_path):
    if file_path.suffix.lower()== ".txt":
        return file_path.read_text(encoding="utf-8")

    elif file_path.suffix.lower()==".pdf":
        pdf= fitz.open(file_path)

        text=""
        for page in pdf:
            text+= page.get_text()

        pdf.close()
        return text

    elif file_path.suffix.lower()==".docx":
        document= Document(file_path)
        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    else:
        return None


def load_documents(data_folder="data"):
    data_folder= Path(data_folder)
    documents=[]
    for file_path in data_folder.iterdir():
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in [".txt", ".pdf", ".docx"]:
            continue
        text= extract_text(file_path)
        documents.append({
            "text": text,
            "source": file_path.name
        })
    

    print("Documents loaded ", len(documents))

    for document in documents:
        print("Source: ", document["source"])

    return documents


def create_chunks(documents, chunk_size=500, overlap=100):
    chunks=[]
    for document in documents:
        start=0
        text= document["text"]
        source= document["source"]

        while start<len(text):
            end= start+chunk_size
            chunk_text= text[start:end]
            chunks.append({
                "text": chunk_text,
                "source": source
            })
            start= end-overlap
    print("Total Chunks: ", len(chunks))

    for chunk in chunks[:5]:
        print("\n\nSource: ", chunk["source"])
        print("Text: ", chunk["text"][:100])

    return chunks