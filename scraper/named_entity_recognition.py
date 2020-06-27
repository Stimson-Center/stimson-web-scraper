import json
from collections import OrderedDict

import numpy as np
from spacy.lang.en.stop_words import STOP_WORDS


# import requests
# from bs4 import BeautifulSoup
#
#
# def url_to_string(url):
#     res = requests.get(url)
#     html = res.text
#     soup = BeautifulSoup(html, 'html5lib')
#     for script in soup(["script", "style", 'aside']):
#         script.extract()
#     return " ".join(re.split(r'[\n\t]+', soup.get_text()))


# nlp = en_core_web_sm.load()
# doc = nlp(
#     'European authorities fined Google a record $5.1 billion on Wednesday for abusing its power in the mobile phone market and ordered the company to alter its practices')
# pprint([(X.text, X.label_) for X in doc.ents])
# pprint([(X, X.ent_iob_, X.ent_type_) for X in doc])
#
# ny_bb = url_to_string(
#     'https://www.nytimes.com/2018/08/13/us/politics/peter-strzok-fired-fbi.html?hp&action=click&pgtype=Homepage&clickSource=story-heading&module=first-column-region&region=top-news&WT.nav=top-news')
# article = nlp(ny_bb)
# len(article.ents)
#
# labels = [x.label_ for x in article.ents]
# Counter(labels)
#
# items = [x.text for x in article.ents]
# Counter(items).most_common(3)
#
# sentences = [x for x in article.sents]
# print(sentences[20])
#
# x = dict([(str(x), x.label_) for x in nlp(str(sentences[20])).ents])
# print([(x, x.ent_iob_, x.ent_type_) for x in sentences[20]])


def pretty_print(obj, indent=False):
    """
    pretty print a JSON object
    """

    if indent:
        return json.dumps(obj, sort_keys=True, indent=2, separators=(',', ': '))
    else:
        return json.dumps(obj, sort_keys=True)


# https://gist.github.com/BrambleXu/3d47bbdbd1ee4e6fc695b0ddb88cbf99
# https://spacy.io/usage/linguistic-features
# https://spacy.io/api/doc
class TextRank4Keyword:
    """Extract keywords from text"""

    def __init__(self, nlp):
        self.nlp = nlp
        self.d = 0.85  # damping coefficient, usually is .85
        self.min_diff = 1e-5  # convergence threshold
        self.steps = 10  # iteration steps
        self.node_weight = None  # save keywords and its weight
        self.doc = None

    def set_stopwords(self, stopwords):
        """Set stop words"""
        for word in STOP_WORDS.union(set(stopwords)):
            lexeme = self.nlp.vocab[word]
            lexeme.is_stop = True

    def sentence_segment(self, candidate_pos, lower):
        """Store those words only in cadidate_pos"""
        sentences = []
        for sent in self.doc.sents:
            selected_words = []
            for token in sent:
                # Store words only with cadidate POS tag
                if token.pos_ in candidate_pos and token.is_stop is False:
                    if lower is True:
                        selected_words.append(token.text.lower())
                    else:
                        selected_words.append(token.text)
            sentences.append(selected_words)
        return sentences

    def get_vocab(self, sentences):
        """Get all tokens"""
        vocab = OrderedDict()
        i = 0
        for sentence in sentences:
            for word in sentence:
                if word not in vocab:
                    vocab[word] = i
                    i += 1
        return vocab

    def get_token_pairs(self, window_size, sentences):
        """Build token_pairs from windows in sentences"""
        token_pairs = list()
        for sentence in sentences:
            for i, word in enumerate(sentence):
                for j in range(i + 1, i + window_size):
                    if j >= len(sentence):
                        break
                    pair = (word, sentence[j])
                    if pair not in token_pairs:
                        token_pairs.append(pair)
        return token_pairs

    def symmetrize(self, a):
        return a + a.T - np.diag(a.diagonal())

    def get_matrix(self, vocab, token_pairs):
        """Get normalized matrix"""
        # Build matrix
        vocab_size = len(vocab)
        g = np.zeros((vocab_size, vocab_size), dtype='float')
        for word1, word2 in token_pairs:
            i, j = vocab[word1], vocab[word2]
            g[i][j] = 1

        # Get Symmeric matrix
        g = self.symmetrize(g)

        # Normalize matrix by column
        norm = np.sum(g, axis=0)
        g_norm = np.divide(g, norm, where=norm != 0)  # this is ignore the 0 element in norm

        return g_norm

    def get_keywords(self, number=10):
        """Print top number keywords"""
        node_weight = OrderedDict(sorted(self.node_weight.items(), key=lambda t: t[1], reverse=True))
        keywords = dict()
        for i, (k, v) in enumerate(node_weight.items()):
            keywords[k] = v
            if i > number:
                break
        return keywords

    def get_phrases(self, number=10):
        phrases = list()
        for i, p in enumerate(self.doc._.phrases):
            if i >= number:
                break
            phrases.append(p)
        return phrases

    def get_sentences(self, number=5):
        sentences = list()
        for i, s in enumerate(self.doc.sents):
            if i >= number:
                break
            sentences.append(s)
        return sentences

    def analyze(self, text, candidate_pos=None, window_size=4, lower=False, stopwords=None):
        """Main function to analyze text"""

        # Set stop words
        if stopwords is None:
            stopwords = list()
        if candidate_pos is None:
            candidate_pos = ['NOUN', 'PROPN']
        self.set_stopwords(stopwords)

        # Pare text by spaCy
        self.doc = self.nlp(text)

        # Filter sentences
        sentences = self.sentence_segment(candidate_pos, lower)  # list of list of words

        # Build vocabulary
        vocab = self.get_vocab(sentences)

        # Get token_pairs from windows
        token_pairs = self.get_token_pairs(window_size, sentences)

        # Get normalized matrix
        g = self.get_matrix(vocab, token_pairs)

        # Initionlization for weight(pagerank value)
        pr = np.array([1] * len(vocab))

        # Iteration
        previous_pr = 0
        for epoch in range(self.steps):
            pr = (1 - self.d) + self.d * np.dot(g, pr)
            if abs(previous_pr - sum(pr)) < self.min_diff:
                break
            else:
                previous_pr = sum(pr)

        # Get weight for each node
        node_weight = dict()
        for word, index in vocab.items():
            node_weight[word] = pr[index]

        self.node_weight = node_weight
