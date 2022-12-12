from pathlib import Path
from typing import Generator
import pandas as pd
import numpy as np

import dhlab as dh
from dhlab.api.dhlab_api import urn_collocation, get_document_frequencies, collocation, word_variant, word_paradigm
from dhlab.text.utils import urnlist


# Helper functions
def count_sentiment_tokens(coll: pd.DataFrame, terms: pd.Series) -> pd.DataFrame:
    """Combine collocation counts with a series of terms (positive or negative)."""
    target_terms = terms.join(coll, how="inner", on="terms")
    return target_terms


def group_index_terms(df: pd.DataFrame) -> pd.DataFrame:
    """Group duplicate index terms, make them case-insensitive, and sum up their frequency counts."""
    df.index = df.index.str.lower()
    df.index.name = "index"
    df = df.groupby('index')["counts"].sum().to_frame("counts")
    assert df.index.is_unique, "There are duplicate collocation terms after case-insensitive transformation."
    return df


def make_list(value) -> list:
    """Turn a string or list into a list.

    :param value: Can be a list, a single valued string, a comma-separated string of values,
        or a multiline string of values separated by newline.
    """
    if isinstance(value, str):
        if value.__contains__("\n"):
            newlist = value.strip("\n").strip().split("\n")
        elif value.__contains__(","):
            newlist = value.split(",")
        else:
            newlist = [value]
        return [v.strip() for v in newlist]
    else:
        assert isinstance(value, list)
        return value

def load_corpus_from_file(file_path):
    """Load a Corpus object from an excel or csv file."""
    try:
        corpus = dh.Corpus.from_df(pd.read_excel(file_path)) if file_path.endswith(".xlsx") else dh.Corpus.from_csv(file_path)
    except FileNotFoundError:
        print("The corpus file must be a .csv or .xlsx file: ", file_path)
        corpus = dh.Corpus()
    return corpus


def load_sentiment_terms(fpath: str = None, sentiment="Positive") -> pd.Series:
    """Load a sentiment lexicon from file.

     By defalt, use the Positive sentiment lexicon from [``ǸorsentLex``](https://github.com/ltgoslo/norsentlex).

     - [Lexicon information in neural sentiment analysis:
     a multi-task learning approach](https://aclanthology.org/W19-6119) (Barnes et al., NoDaLiDa 2019)
    """
    if fpath is None or not Path(fpath).exists:
        fpath =  f"https://raw.githubusercontent.com/ltgoslo/norsentlex/master/Fullform/Fullform_{sentiment}_lexicon.txt"
    return pd.read_csv(fpath, names=["terms"])


def timestamp_generator(from_year: int, to_year: int) -> Generator:
    """Generate a timestamp per day in the period ``from_year``-``to_year``."""
    # range of timestamps
    timestamp_range = pd.date_range(start=f"{from_year}-01-01", end=f"{to_year}-12-31")

    for i in timestamp_range:
        date = "".join(str(i).split()[0].split("-"))
        yield date


def strip_empty_cols(dhobj):
    """Remove columns without values from a DhlabObj."""
    return dhobj.frame.dropna(axis=1, how="all").fillna("")


def coll_sentiment(coll, word="barnevern", return_score_only=False):
    """Compute a sentiment score of positive and negative terms in `coll`.

    The collocations of the ``word`` are used to count occurrences of positive and negative terms.

    :param coll: a collocations dataframe or a dh.Corpus where `word` occurs.
    :param str word: a word to estimate sentiment scores for
    :param bool return_score_only: If True,
        return a tuple with the absolute counts for positive and negative terms.
    """
    if isinstance(coll, dh.Corpus):
        coll = coll.coll(word).frame

    coll = group_index_terms(coll)

    # Data import
    pos = load_sentiment_terms(sentiment="Positive")
    neg = load_sentiment_terms(sentiment="Negative")

    positive_counts = count_sentiment_tokens(coll, pos)
    negative_counts = count_sentiment_tokens(coll, neg)

    if return_score_only:
        return positive_counts.counts.sum(), negative_counts.counts.sum()

    neutral_counts = coll.join(
        pd.DataFrame(
            pd.concat(
                [coll, negative_counts, positive_counts]
                ).index.drop_duplicates(keep=False)
            ).set_index(0),
        how="inner"
        )

    positive_counts["sentiment"] = "pos"
    negative_counts["sentiment"] = "neg"
    neutral_counts["sentiment"] = "neutral"

    return pd.concat([positive_counts, negative_counts, neutral_counts])


def sentiment_by_place(keyword:str ="barnevern", cities=["Kristiansand", "Stavanger"], from_year=1999, to_year=2010):

    cities = make_list(cities)
    for city in cities:
        lst = []
        for year in range(from_year, to_year):
            corpus = dh.Corpus(doctype="digavis", freetext=f"city: {city} year: {year}", limit=1000)
            pos, neg = coll_sentiment(corpus, keyword, return_score_only=True)

            lst.append(
                pd.DataFrame(
                    [[pos, neg, pos-neg]],
                    index=[year],
                    columns=["positive", "negative", "sum"]
                    )
                )

        yield pd.concat(lst)


def fetch_finegrained_collocations(urn: str, word: str, before: int, after: int) -> pd.DataFrame:
    """For a given URN and a given word, fetch collocations with """

    coll = urn_collocation(
        urns=[urn],
        word=word,
        before=before,
        after=after
    )
    coll = coll.loc[[x for x in coll.index if x.isalpha()]]
    coll.index = [x.lower() for x in coll.index]
    coll = coll.groupby(coll.index).sum()
    return coll


def score_sentiment(urn, word, before, after):
    """Calculate a sentiment score for the contexts of ``word`` in a given publication (``URN``)."""
    collocations = fetch_finegrained_collocations(urn, word, before, after)
    pos, neg = coll_sentiment(collocations,return_score_only=True)
    values = [urn, word, pos, neg, pos-neg]
    names = ["urn", "target_word", "positive", "negative", "sentimentscore"]
    return dict(zip(names, values))



def unpivot(frame):
    """Reshape a dataframe with multiple indexes.

    Util function copied from Pandas docs:
    https://pandas.pydata.org/pandas-docs/stable/user_guide/reshaping.html
    """
    N, K = frame.shape
    data = {
        "frequency": frame.to_numpy().ravel("F"),
        "urn": np.asarray(frame.columns).repeat(N),
        "word": np.tile(np.asarray(frame.index), K),
    }

    return pd.DataFrame(data, columns=["word", "urn", "frequency"])



def score_sentiment(urn, word, before, after):
    """Calculate a sentiment score for the contexts of ``word`` in a given publication."""
    collocations = fetch_finegrained_collocations(urn, word, before, after)
    pos, neg = coll_sentiment(collocations, word, return_score_only=True)
    values = [pos, neg, pos-neg]
    names = ["positive", "negative", "sentimentscore"]
    return dict(zip(names, values))


def count_and_score_target_word(corpus: dh.Corpus, search_terms: str):
    words = make_list(search_terms)
    counts = corpus.count(words)
    term_counts = unpivot(counts.frame)
    scored_terms = term_counts.apply(lambda x: score_sentiment(x.urn, x.word, before, after ), axis=1, result_type="expand")
    term_counts.loc[:, ["positive", "negative", "sentimentscore"]] = scored_terms
    df = strip_empty_cols(corpus)
    return df.merge(term_counts, how="inner", left_on="urn", right_on="urn")
