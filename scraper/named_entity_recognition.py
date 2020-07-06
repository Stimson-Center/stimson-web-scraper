import json
import re
from collections import OrderedDict
from date_extractor import extract_dates, extract_date, isDefinitelyNotDate
import dateparser
import numpy as np
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.matcher import Matcher


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
        # initialize matcher with a vocab
        self.matcher = Matcher(nlp.vocab)
        self.d = 0.85  # damping coefficient, usually is .85
        self.min_diff = 1e-5  # convergence threshold
        self.steps = 10  # iteration steps
        self.node_weight = None  # save keywords and its weight
        self.doc = None
        self.stopwords = STOP_WORDS

    def set_stopwords(self, stopwords):
        """
        Set stop words
        """
        self.stopwords = self.stopwords.union(set(stopwords))
        for word in self.stopwords:
            lexeme = self.nlp.vocab[word]
            lexeme.is_stop = True

    def sentence_segment(self, candidate_pos, lower):
        """
        Store those words only in cadidate_pos
        """
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
        """
        Get all tokens
        """
        vocab = OrderedDict()
        i = 0
        for sentence in sentences:
            for word in sentence:
                if word not in vocab:
                    vocab[word] = i
                    i += 1
        return vocab

    def get_token_pairs(self, window_size, sentences):
        """
        Build token_pairs from windows in sentences
        """
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

    @staticmethod
    def symmetrize(a):
        return a + a.T - np.diag(a.diagonal())

    def get_matrix(self, vocab, token_pairs):
        """
        Get normalized matrix
        """
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
        """
        Print top number keywords
        """
        node_weight = OrderedDict(sorted(self.node_weight.items(), key=lambda t: t[1], reverse=True))
        keywords = dict()
        for i, (k, v) in enumerate(node_weight.items()):
            if k.isalnum():
                keywords[k] = v
                if i > number:
                    break
        return keywords

    def get_phrases(self, number=10):
        phrases = list()
        # noinspection PyProtectedMember
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

    def get_dates(self):
        # https://spacy.io/usage/linguistic-features#101
        ents = [ent for ent in self.doc.ents if ent.label_ == 'DATE']
        for ent in self.doc.ents:
            if ent.label_ == "01/04/1937":
                pass
        dates = list()
        for ent in ents:
            date = dateparser.parse(ent.text)
            dates.append(date)
        if not dates:
            extracted_dates = extract_dates(self.doc.text)
            dates += extracted_dates
        return dates

    def get_persons(self):
        # https://omkarpathak.in/2018/12/18/writing-your-own-resume-parser/#rule-based-matching
        # First name and Last name are always Proper Nouns
        # pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        # self.matcher.add('NAME', None, pattern)
        # matches = self.matcher(self.doc)
        # persons = list()
        # for match_id, start, end in matches:
        #     span = self.doc[start:end]
        #     persons.append(span.text)
        # return persons
        return [ent.text for ent in self.doc.ents if ent.label_ == 'PERSON']


    def get_education(self):
        # https://omkarpathak.in/2018/12/18/writing-your-own-resume-parser/#rule-based-matching
        # Education Degrees
        # noinspection PyPep8Naming
        EDUCATION = [
            'BE', 'B.E.', 'B.E',
            'BS', 'B.S.', 'B.S',
            'BA', 'B.A', 'B.A',
            'ME', 'M.E.', 'M.E',
            'MS', 'M.S.', 'M.S'
                          'BTECH', 'B.TECH',
            'M.TECH', 'MTECH',
            'PhD', 'Ph.D.', 'Ph.D', 'DPhil',
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
        ]
        # Sentence Tokenizer
        nlp_text = [sent.string.strip() for sent in self.doc.sents]
        edu = dict()
        # Extract education degree
        for index, text in enumerate(nlp_text):
            for tex in text.split():
                # Replace all special symbols
                tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                if tex.upper() in EDUCATION and tex not in self.stopwords:
                    edu[tex] = text + nlp_text[index + 1]

        # Extract year
        education = []
        for key in edu.keys():
            year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
            if year:
                education.append((key, ''.join(year[0])))
            else:
                education.append(key)
        return education

    def analyze(self, text, candidate_pos=None, window_size=4, lower=False, stopwords=None):
        """
        Main function to analyze text
        """

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

        # Initialization for weight(pagerank value)
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
