from pathlib import Path

def load_documents(data_folder="data"):
    data_folder= Path(data_folder)
    documents=[]
    for file_path in data_folder.glob("*.txt"):
        text= file_path.read_text(encoding="utf-8")
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