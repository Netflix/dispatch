import logging
from typing import List

import spacy
from spacy.matcher import PhraseMatcher

log = logging.getLogger(__name__)

nlp = spacy.blank("en")
nlp.vocab.lex_attr_getters = {}


def build_term_vocab(terms: List[str]):
    """Builds nlp vocabulary."""
    for v in terms:
        texts = [v, v.lower(), v.upper(), v.title()]
        for t in texts:
            if t:  # guard against `None`
                phrase = nlp.tokenizer(t)
                for w in phrase:
                    _ = nlp.tokenizer.vocab[w.text]
                    yield phrase


def build_phrase_matcher(name: str, phrases: List[str]) -> PhraseMatcher:
    """Builds a PhraseMatcher object."""
    matcher = PhraseMatcher(nlp.tokenizer.vocab)
    matcher.add(name, phrases)
    return matcher


def extract_terms_from_text(text: str, matcher: PhraseMatcher) -> List[str]:
    """Extracts key terms out of test."""
    terms = []
    doc = nlp.tokenizer(text)
    for w in doc:
        _ = doc.vocab[
            w.text.lower()
        ]  # We normalize our docs so that vocab doesn't take so long to build.

    matches = matcher(doc)
    for _, start, end in matches:
        with doc.retokenize() as retokenizer:
            retokenizer.merge(doc[start:end])

        # We try to filter out common stop words unless
        # we have surrounding context that would suggest they are not stop words.
        span = doc[start:end]
        for token in span:
            if token.is_stop:
                continue

            terms.append(token.text.lower())

    return terms
