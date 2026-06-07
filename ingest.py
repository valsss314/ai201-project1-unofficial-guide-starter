"""
Milestone 3 — Document ingestion + chunking pipeline.

Domain: student reviews of Georgia Tech CS professors, copied from RateMyProfessors.

Each professors/profN.txt file is the *rendered text* of one RMP page. It has three parts:
  1. Top nav boilerplate  (Logo, Professors, Log In, ...)
  2. A professor header    (name, department, school, overall stats, rating distribution)
  3. A list of reviews     (each a fixed Quality/Difficulty/metadata/prose/tags template)
  4. Bottom footer         (Site Guidelines, Terms, (c) Rate My Professors ...)

Chunking strategy: ONE REVIEW = ONE CHUNK.
Each RMP review is already a short, self-contained student opinion, so the natural
chunk boundary is the review itself -- no fixed character splitting, no overlap.
We attach the professor name, course, quality, difficulty, grade, and date to every
chunk so it can be retrieved and understood on its own.
"""

import os
import re
import glob

DOCS_DIR = "professors"

# Lines whose text before the colon is one of these are review *metadata*, not prose.
META_KEYS = {
    "For Credit",
    "Attendance",
    "Would Take Again",
    "Grade",
    "Textbook",
    "Online Class",
    "Reviewed",
}


def load_documents(docs_dir=DOCS_DIR):
    """Load every .txt file as a list of stripped, non-empty lines."""
    docs = {}
    for path in sorted(glob.glob(os.path.join(docs_dir, "*.txt"))):
        with open(path, encoding="utf-8") as f:
            lines = [ln.strip() for ln in f]
        docs[os.path.basename(path)] = lines
    return docs


def professor_name(lines):
    """The professor name sits two lines above 'Georgia Institute of Technology'."""
    for i, ln in enumerate(lines):
        if ln == "Georgia Institute of Technology" and i >= 2:
            return lines[i - 2]
    return "Unknown"


def is_quality_marker(lines, i):
    """True if a review block starts at index i: 'Quality' / <number> / 'Difficulty'."""
    return (
        i + 2 < len(lines)
        and lines[i] == "Quality"
        and re.fullmatch(r"\d(\.\d)?", lines[i + 1] or "")
        and lines[i + 2] == "Difficulty"
    )


def split_key_value(line):
    """If a line is 'Key: Value' with a known key, return (key, value); else None."""
    if ": " in line:
        key, value = line.split(": ", 1)
        if key in META_KEYS:
            return key, value
    return None


def parse_reviews(lines, source, name):
    """Turn one document's lines into a list of structured review dicts."""
    # Find where each review block starts.
    starts = [i for i in range(len(lines)) if is_quality_marker(lines, i)]
    reviews = []

    for b, start in enumerate(starts):
        end = starts[b + 1] if b + 1 < len(starts) else len(lines)
        block = [ln for ln in lines[start:end] if ln]  # drop blank lines

        # block[0]='Quality', block[1]=<q>, block[2]='Difficulty', block[3]=<d>
        quality = block[1]
        difficulty = block[3]

        rest = block[4:]
        # First non-"Reviewed:" line is the course code; strip a 'Computer Icon' prefix.
        idx = 0
        while idx < len(rest) and rest[idx].startswith("Reviewed:"):
            idx += 1
        course = re.sub(r"^Computer Icon", "", rest[idx]) if idx < len(rest) else ""
        date = rest[idx + 1] if idx + 1 < len(rest) else ""

        # Walk the metadata fields, then the first non-metadata line is the review prose.
        meta = {}
        j = idx + 2
        while j < len(rest) and split_key_value(rest[j]):
            k, v = split_key_value(rest[j])
            meta[k] = v
            j += 1

        review_text = rest[j] if j < len(rest) else ""
        # Everything after the prose up to the Thumbs counters are student tags.
        tags = []
        for ln in rest[j + 1:]:
            if ln.startswith("Thumbs"):
                break
            tags.append(ln)

        # Skip anything that didn't yield real prose (e.g. a malformed block).
        if len(review_text) < 15:
            continue

        reviews.append({
            "professor": name,
            "course": course,
            "quality": quality,
            "difficulty": difficulty,
            "grade": meta.get("Grade", ""),
            "date": date,
            "tags": tags,
            "text": review_text,
            "source": source,
        })

    return reviews


def to_chunk(r):
    """Compose a self-contained chunk string from a review dict."""
    header = (
        f"Professor {r['professor']} | Course: {r['course']} | "
        f"Quality: {r['quality']}/5, Difficulty: {r['difficulty']}/5"
    )
    if r["grade"]:
        header += f", Grade: {r['grade']}"
    if r["date"]:
        header += f" (reviewed {r['date']})"
    chunk = f"{header}\nReview: {r['text']}"
    if r["tags"]:
        chunk += f"\nStudent tags: {', '.join(r['tags'])}"
    return chunk


def build_chunks():
    """Run the full pipeline: load -> parse -> chunk."""
    docs = load_documents()
    all_reviews = []
    for source, lines in docs.items():
        name = professor_name(lines)
        reviews = parse_reviews(lines, source, name)
        all_reviews.append((source, name, reviews))
    return all_reviews


if __name__ == "__main__":
    all_reviews = build_chunks()

    print("=" * 70)
    print("PER-DOCUMENT REVIEW COUNTS")
    print("=" * 70)
    total = 0
    chunks = []
    for source, name, reviews in all_reviews:
        print(f"  {source:14s} {name:22s} {len(reviews):3d} reviews")
        total += len(reviews)
        chunks.extend(to_chunk(r) for r in reviews)

    print("-" * 70)
    print(f"  TOTAL CHUNKS: {total}")
    print()

    print("=" * 70)
    print("5 REPRESENTATIVE CHUNKS (inspect: is each self-contained?)")
    print("=" * 70)
    # Spread the samples across the corpus instead of taking the first 5.
    step = max(1, len(chunks) // 5)
    for n, idx in enumerate(range(0, len(chunks), step)):
        if n == 5:
            break
        print(f"\n--- chunk #{idx} ({len(chunks[idx])} chars) ---")
        print(chunks[idx])
