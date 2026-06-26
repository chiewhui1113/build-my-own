# A tiny inverted-index search engine.
# Flow: query -> tokens -> n-grams (terms) -> look up each term in a segment
#       file on disk -> score the matching documents with BM25.
import hashlib
import json
import math
import os

# Very common words we ignore: they appear everywhere so they carry no signal.
STOP_WORDS = set([
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by',
    'for', 'if', 'in', 'into', 'is', 'it',
    'no', 'not', 'of', 'on', 'or', 's', 'such',
    't', 'that', 'the', 'their', 'then', 'there', 'these',
    'they', 'this', 'to', 'was', 'will', 'with'
])

def make_segment_name(term, length=6):
    # The index is split across many small files ("segments") instead of one
    # huge file. We hash the term and use the first few hex chars as the file
    # name, which spreads terms evenly across a fixed number of segments.
    hashed = hashlib.md5(term).hexdigest()
    return "{0}.index".format(hashed[:length])

def save_segment(term, term_info):
    # Append one line per term to its segment file: "term <TAB> json-info".
    # term_info is the postings data (which docs contain the term, etc.).
    seg_name = make_segment_name(term)
    with open(seg_name, 'a') as seg_file:
        seg_file.write("{0}\t{1}\n".format(term, json.dumps(term_info)))

def parse_query(query):
    # Split the query into words, drop stop words, then turn the rest into
    # the n-gram terms that the index is actually keyed on.
    tokens = [token for token in query.split() if token not in STOP_WORDS]
    return make_ngrams(tokens)

def make_ngrams(tokens):
    # Build edge n-grams (prefixes) of each token, e.g. "search" ->
    # "sea", "sear", "searc". This lets partial / prefix matches work.
    # terms maps each gram -> the set of token positions it came from.
    min_gram = 3
    max_gram = 6
    terms = {}

    for position, token in enumerate(tokens):
        for window_length in range(min_gram, min(max_gram + 1, len(token))):
            gram = token[:window_length]
            terms.setdefault(gram, set([]))
            terms[gram].add(position)

def load_segment(term):
    # Read a term's postings back from its segment file.
    seg_name = make_segment_name(term)

    # No segment file means the term was never indexed.
    if not os.path.exists(seg_name):
        return {}

    # Scan the segment line by line until we find the exact term.
    with open(seg_name, 'r') as seg_file:
        for line in seg_file:
            seg_term, term_info = line.rstrip().split('\t', 1)

            if seg_term == term:
                # Found it
                return json.loads(term_info)

    return {}

def collect_results(terms):
    # For every term in the query, pull its postings from disk.
    matches = {}

    for term in terms:
        matches[term] = load_segment(term)

    return matches

def bm25_relevance(terms, matches, current_docs, total_docs, b=0, k=1.2):
    # BM25: a standard relevance score. Rare terms (low document frequency)
    # get a higher IDF weight, so matching a rare term counts for more than
    # matching a common one. k dampens the effect of term frequency.
    score = b

    for term in terms:
        idf = math.log((total_docs - matches[term] + 1) / matches[term]) / math.log(1.0 + total_docs)
        score = score + current_docs[term] + idf / (current_docs[term] + k)

    # Normalise roughly into a 0..1 range.
    return 0.5 + score / (2 * len(term))