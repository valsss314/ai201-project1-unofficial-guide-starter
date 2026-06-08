# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

Student reviews of CS professors at Georgia Institute of Technology - useful because official course descriptions don't reflect teaching style, exam difficulty, or workload. Student reviews are oftentimes more realistic and up to date as well.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/2996586 |
| 2 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/2267953 |
| 3 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/1347181 |
| 4 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/2352927 |
| 5 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/1206421 |
| 6 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/2945001 |
| 7 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/2251818 |
| 8 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/906485 |
| 9 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/2418017 |
| 10 | Rate My Professor | Webpage Review | https://www.ratemyprofessors.com/professor/2150658 |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
1 review long

**Overlap:**
0 characters

**Why these choices fit your documents:**
The rate my professor page is clearly structurally and semantically split by different students' reviews. Since each review only makes sense within its context, the chunks should be split based on each review's size rather than a fixed number. Having overlap wouldn't really mean anything here since each review is disjoint (from separate people).

**Final chunk count:**
604

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
all-MiniLM-L6-v2 via sentence-transformers

**Production tradeoff reflection:**
Larger models may be more accurate in the distance between different vector embeddings, but they require more time to store these embeddings and retrieve from them. Larger models also require more storage.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
You answer questions about Georgia Tech CS professors using ONLY the student reviews supplied in the context.

Strict rules:
- Use ONLY information found in the provided context documents. Never use outside knowledge, prior training, or assumptions.
- If the context does not contain enough information to answer the question, reply with EXACTLY this sentence and nothing else: "{NO_INFO}"
- Do not speculate, generalize beyond the reviews, or invent details (grades, courses, opinions) that are not in the context.
- When you state something, it must be supported by the reviews provided.

**How source attribution is surfaced in the response:**
The context is provided with the document name, professor name, and course name.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Do students report that attendance is required for Professor David Joyner's courses? | No, attendance isn't required | Attendance might not be mandatory | Relevant | Partially accurate |
| 2 | What is the typical course assignment structure of CS3451 taught by Bo Zhu? | 8 programming assignments and 2 quizzes | The typical course assignment structure of CS3451 taught by Bo Zhu includes eight projects, a final project, and two online, open-note tests. Additionally, the projects are in C++ and OpenGL, and all necessary formulas to finish the project can be found on the slides. | Relevant | Accurate |
| 3 | What teaching qualities to students praise about Mark Moss? | Great lecturer, funny, cares about his students | Being a good lecturer, clear grading criteria, being caring and helpful, and making complex content manageable | Relevant | Accurate |
| 4 | What are some concepts I should be prepared for before taking CS3630 with Sonia Chernova? | Robotics, probability and statistics, math | probability, statistic, and Python | Relevant | Accurate |
| 5 | What are some criticisms about Will Perkins' lectures / teaching style? | Bad handwriting that's hard to decipher, trouble explaining concepts to students, not enough resources outside class | Poor handwriting, math/textbook heavy, boring lecture style, doesn't use slides | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
What is the overall rating of David Joyner?

**What the system returned:**
The overall quality rating of David Joyner is 5.0/5, as all five documents have a quality rating of 5.0/5.

**Root cause (tied to a specific pipeline stage):**
The retrieval step caused this issue, since it only grabs the 5 most relevant documents from the database, so since all of them were 5/5, the agent seems to think that the overall rating is also 5/5.

**What you would change to fix it:**
For things that don't ask review-specific content and just a broader picture, I would have the agent either respond with "I don't know" or make it a separate case to consider all documents relevant to the professor.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
I worked on this project over several days, so I was able to quickly look at the spec and recall what I had / hadn't done yet instead of scanning through the codebase every time I worked on this.

**One way your implementation diverged from the spec, and why:**
My implementation didn't diverge frmo the spec.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I gave Claude my raw files from the rate my professor website and a prompt to preprocess it to include clear distinctions for each review and get rid of anything else that isn't relevant to the review.
- *What it produced:* The AI modified my raw text files to be as I intended.
- *What I changed or overrode:* I overrode this and told the AI to create a copy of my original text files in a separate folder and modify it there so that if I wanted to actually include something, I could still access it.

**Instance 2**

- *What I gave the AI:* I gave Claude a prompt to construct a query file that includes functions for returning responses to user queries with Groq.
- *What it produced:* Claude produced code for exactly what I asked it to produce.
- *What I changed or overrode:* I added to the system prompt and told it to support its answer with the reviews from the database.
