import logging
from typing import List

import spacy
from spacy.matcher import PhraseMatcher

log = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_sm")
nlp.vocab.lex_attr_getters = {}


# NOTE
# This is kinda slow so we might cheat and just build this
# periodically or cache it
def build_term_vocab(terms: List[str]):
    """Builds nlp vocabulary."""
    # We need to build four sets of vocabulary
    # such that we can more accurately match
    #
    # - No change
    # - Lower
    # - Upper
    # - Title
    #
    # We may also normalize the document itself at some point
    # but it unclear how this will affect the things like
    # Parts-of-speech (POS) analysis.
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
    matcher.add(name, None, *phrases)  # TODO customize
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
        token = doc[start:end].merge()

        # We try to filter out common stop words unless
        # we have surrounding context that would suggest they are not stop words.
        if token.is_stop:
            continue

        terms.append(token.text)

    return terms
