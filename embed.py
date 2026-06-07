"""
Milestone 4 — Embedding + retrieval.

Pipeline stage 3 & 4 of the architecture:
  Chunking (ingest.build_chunks)  ->  Embedding + Vector Store (this file)  ->  Retrieval

We embed every review chunk with all-MiniLM-L6-v2 (local, no API key, 384-dim) and
store it in a persistent ChromaDB collection along with source metadata so we can
attribute answers later. retrieve() returns the top-k nearest chunks for a query.

Distance metric: cosine. Embeddings are L2-normalized, so ChromaDB's cosine distance
falls in [0, 2] where ~0 = near-identical and >0.6-0.7 = weak match.
"""

from sentence_transformers import SentenceTransformer
import chromadb

from ingest import build_chunks, to_chunk

MODEL_NAME = "all-MiniLM-L6-v2"
DB_PATH = "chroma_db"
COLLECTION_NAME = "professor_reviews"

# Cache the model so repeated retrieve() calls don't reload it.
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def build_index(reset=True):
    """Embed all chunks and (re)load them into ChromaDB with metadata."""
    model = get_model()
    client = chromadb.PersistentClient(path=DB_PATH)

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # collection didn't exist yet

    collection = client.get_or_create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )

    ids, documents, metadatas = [], [], []
    for source, name, reviews in build_chunks():
        for position, r in enumerate(reviews):
            ids.append(f"{source}:{position}")
            documents.append(to_chunk(r))
            metadatas.append({
                "source": source,            # which document this chunk came from
                "position": position,        # chunk's position within that document
                "professor": name,
                "course": r["course"],
                "quality": float(r["quality"]),
                "difficulty": float(r["difficulty"]),
                "grade": r["grade"],
                "date": r["date"],
            })

    # normalize_embeddings=True pairs with the cosine space set above.
    embeddings = model.encode(
        documents, show_progress_bar=True, normalize_embeddings=True
    ).tolist()

    collection.add(
        ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
    )
    print(f"Indexed {collection.count()} chunks into '{COLLECTION_NAME}'.")
    return collection


def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_collection(COLLECTION_NAME)


def retrieve(query, k=5, collection=None):
    """Return the top-k most relevant chunks for a query.

    Each hit is {text, distance, source, professor, course, ...}.
    """
    model = get_model()
    collection = collection or get_collection()
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()

    res = collection.query(query_embeddings=query_embedding, n_results=k)

    hits = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append({"text": doc, "distance": dist, **meta})
    return hits


# A few starter queries spanning the corpus (refine these in your evaluation plan).
TEST_QUERIES = [
    "Which professor is a tough grader who doesn't give a clear rubric?",
    "What do students say about David Joyner's online CS1301 class?",
    "Is Sonia Chernova's robotics class hard, and how is it graded?",
]


if __name__ == "__main__":
    build_index(reset=True)
    print()
    for q in TEST_QUERIES:
        print("=" * 78)
        print(f"QUERY: {q}")
        print("=" * 78)
        for rank, h in enumerate(retrieve(q, k=5), 1):
            preview = h["text"].replace("\n", " ")
            if len(preview) > 160:
                preview = preview[:160] + "..."
            print(f"\n[{rank}] distance={h['distance']:.3f}  source={h['source']}  "
                  f"prof={h['professor']}  course={h['course']}")
            print(f"    {preview}")
        print()
