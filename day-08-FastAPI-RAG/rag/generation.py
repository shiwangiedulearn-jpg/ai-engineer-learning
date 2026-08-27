from google import genai

def generate_answer(client, query, results):
    context= "\n\n".join(
        result.payload["text"]
        for result in results
    )
    prompt= f"""
    You are a medical information assistant.
    Answer the user's question using only the information provided in the context below.
    The context may contain information from one or more documents. Use all relevant information from the provided context to answer the question.
    If the context doesnot contain enough information to anser the question say:
    "I dont have enough information in the provided documents."
    Do not invent medical facts.
    Context:
    {context}

    User question:
    {query}
    Answer:
    """
    response= client.models.generate_content(
        model= "gemini-3.6-flash",
        contents= prompt
    )
    return response.text