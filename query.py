"""
Milestone 5 — grounded generation.

Pipeline stage 5: Retrieval (embed.retrieve) -> Generation (this file).

ask(question) retrieves the top-k review chunks, passes them to Groq's
llama-3.3-70b-versatile as the ONLY allowed source of truth, and returns
{answer, sources, hits}.

Grounding is enforced two ways:
  1. A system prompt that forbids outside knowledge and mandates a fixed refusal
     string when the context is insufficient.
  2. Source attribution is built PROGRAMMATICALLY from the retrieved chunks'
     metadata -- it is never left to the LLM to invent, so a citation can only
     name a document that was actually retrieved.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from embed import retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
TOP_K = 5
NO_INFO = "I don't have enough information on that."

SYSTEM_PROMPT = f"""You answer questions about Georgia Tech CS professors using ONLY the student reviews supplied in the context.

Strict rules:
- Use ONLY information found in the provided context documents. Never use outside knowledge, prior training, or assumptions.
- If the context does not contain enough information to answer the question, reply with EXACTLY this sentence and nothing else: "{NO_INFO}"
- Do not speculate, generalize beyond the reviews, or invent details (grades, courses, opinions) that are not in the context.
- When you state something, it must be supported by the reviews provided.
"""


def build_context(hits):
    """Format retrieved chunks as numbered, source-labeled context blocks."""
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(
            f"[Document {i} | source: {h['source']} | "
            f"professor: {h['professor']} | course: {h['course']}]\n{h['text']}"
        )
    return "\n\n".join(blocks)


def attribute_sources(hits):
    """Build the source list from metadata (one entry per unique document)."""
    sources, seen = [], set()
    for h in hits:
        if h["source"] not in seen:
            seen.add(h["source"])
            sources.append(f"{h['source']} — {h['professor']}")
    return sources


def ask(question, k=TOP_K, collection=None):
    hits = retrieve(question, k=k, collection=collection)
    context = build_context(hits)

    user_msg = (
        f"Context documents:\n\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above."
    )

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,  # low temp -> stays close to the provided text
    )
    answer = resp.choices[0].message.content.strip()

    # If the model refused, don't attach sources (nothing was actually used).
    sources = [] if answer.strip() == NO_INFO else attribute_sources(hits)

    return {"answer": answer, "sources": sources, "hits": hits}


if __name__ == "__main__":
    tests = [
        "Which professor is known as a tough grader with unclear rubrics?",
        "What do students say about David Joyner's online CS1301 class?",
        "How is Sonia Chernova's robotics class graded?",
        "What are the best dining halls at Georgia Tech?",  # out-of-domain -> should refuse
    ]
    for q in tests:
        print("=" * 80)
        print("Q:", q)
        result = ask(q)
        print("\nANSWER:\n", result["answer"])
        print("\nSOURCES:")
        for s in result["sources"]:
            print("  •", s)
        if not result["sources"]:
            print("  (none — model reported insufficient information)")
        print()
