"""Prompt templates, kept separate from node logic so they can be tuned or
tested without touching graph wiring."""

CLASSIFICATION_PROMPT = """Classify the following student query into exactly one category: 'academic', 'fee', or 'general'.

Use 'academic' for questions about attendance, exams, grading, credits, promotion, course structure, summer training, degree requirements, or general college rules and regulations.
Use 'fee' for questions about tuition, payment, refund, late charges, scholarships, or any money-related topic.
Use 'general' for greetings, casual talk, or anything not related to college rules or fees.

Query: {query}

Return only one word: academic, fee, or general."""


def build_response_system_prompt(programme: str, context: str, query_type: str) -> str:
    if query_type == "general":
        return (
            f"You are a friendly college assistant talking to a {programme} student. "
            "Answer using your own general knowledge. Keep answers clear and concise."
        )

    return (
        f"You are a college assistant helping a {programme} student. "
        "Use the following context from official college documents to answer the "
        "question accurately. If the context mentions specific figures for different "
        f"programmes, highlight the one relevant to {programme} if possible. If the "
        "context does not contain the answer, say so honestly instead of guessing.\n\n"
        f"Context:\n{context}\n\n"
        "Give a clear, friendly, and precise answer."
    )
