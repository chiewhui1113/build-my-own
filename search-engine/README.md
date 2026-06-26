# Build Your Own Search Engine (Python) — Learning Summary

Explains different terminology and flows for a search engine.
Builds an **inverted index** on disk, splits it into hashed **segment** files, 
and ranks results with the **BM25** relevance formula.

**Difficulty:** ⭐ — short and simple, with lively examples.

## How it works

The pipeline goes: query → tokens → n-gram terms → look up each term in its
segment file → score the matching documents.

- **Stop words** — common words like "the", "is", "and" are dropped because they
  appear everywhere and carry no signal.
- **N-grams** (`make_ngrams`) — each token is broken into prefixes
  (e.g. `search` → `sea`, `sear`, `searc`), so partial / prefix matches work.
- **Segments** (`make_segment_name`, `save_segment`, `load_segment`) — instead of
  one giant index file, terms are hashed (MD5) and stored in many small
  `*.index` files. The hash spreads terms evenly across the segments.
- **Postings** — each segment line is `term <TAB> json-info`, where the JSON
  records which documents contain the term.
- **BM25** (`bm25_relevance`) — ranks documents so that matching a *rare* term
  counts more than matching a common one (via IDF), with a `k` factor that
  dampens the effect of term frequency.

## Quick example

Index 3 docs:

```
Doc 1: "The quick brown fox"
Doc 2: "The lazy brown dog"
Doc 3: "A quick brown rabbit"
```

The inverted index (word → docs, stopwords dropped):

```
quick → [1, 3]   brown → [1, 2, 3]   fox → [1]   ...
```

Search `"quick fox"` → look up both terms → candidates: Doc 1, Doc 3. Then rank:
`fox` is rare (1 of 3 docs) so it scores high, `quick` is common (2 of 3) so it
scores low. Doc 1 matches both (including rare `fox`) → ranked first; Doc 3 only
matches `quick` → second. `brown` would be a poor query term: it's in every doc,
so it barely discriminates — the same reason stopwords are dropped entirely.

Source tutorial: [Building a search engine (YouTube)](https://www.youtube.com/watch?v=cY7pE7vX6MU)
