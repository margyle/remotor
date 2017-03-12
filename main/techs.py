"""Identify technologies in job advertisement text.
"""
import json
import os

from nltk import ngrams
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(THIS_DIR, 'tags.json'), 'rb') as f_in:
    tags = json.loads(f_in.read())['tags']


def get_tech(text):
    """Get all technologies from the top 1000 tags on StackOverflow.
    """
    sentences = sent_tokenize(text)
    techs = set()
    for s in sentences:
        tokens = word_tokenize(s)
        techs |= set(tag for tag in tags if tag in tokens)
        bigrams = ['-'.join(ngram) for ngram in ngrams(tokens, 2)]
        techs |= set(tag for tag in tags if tag in bigrams)
        trigrams = ['-'.join(ngram) for ngram in ngrams(tokens, 3)]
        techs |= set(tag for tag in tags if tag in trigrams)
    return list(techs)


def test_get_tech():
    """Test we get all the expected technologies.

    False positives are less important than false negatives.

    """
    text = "python javascript. ruby on rails, objective c"
    techs = get_tech(text)
    assert all(
        t in techs
        for t in ['python', 'javascript', 'ruby-on-rails', 'objective-c']
        )

