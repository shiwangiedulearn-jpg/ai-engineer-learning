from google import genai


def generate_answer(client, query, results):

    context = "\n\n".join(
        result.payload["text"]
        for result in results
    )

    prompt = f"""
You are a research document assistant.

Answer the user's question using only the information
provided in the context below.

The context may contain information from one or more documents.
Use all relevant information from the provided context.

If the context does not contain enough information to answer
the question, say:

"I don't have enough information in the provided documents."

Do not invent information or use knowledge outside the context.

Context:
{context}

User question:
{query}

Answer:
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        generation_config={
            "thinking_level": "low"
        }
    )

    return interaction.output_text