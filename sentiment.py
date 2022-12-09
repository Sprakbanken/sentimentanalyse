import pandas as pd
import dhlab as dh


# Helper functions
def count_sentiment_tokens(coll, terms):
    target_terms = terms.join(coll, how="inner", on="terms")
    return target_terms


def group_index_terms(df):
    df.index = df.index.str.lower()
    df.index.name = "index"
    df = df.groupby('index')["counts"].sum().to_frame("counts")
    assert df.index.is_unique, "There are duplicate collocation terms after case-insensitive transformation."
    return df


def make_list(value):
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



def timestamp_generator(from_year, to_year):
    """Generate a timestamp per day in the period ``from_year``-``to_year``."""
    # range of timestamps
    timestamp_range = pd.date_range(start=f"{from_year}-01-01", end=f"{to_year}-12-31")

    for i in timestamp_range:
        date = "".join(str(i).split()[0].split("-"))
        yield date


def read_spreadsheet(file_path):
    return pd.read_excel(file_path) if file_path.endswith(".xlsx") else pd.read_csv(file_path)


def coll_sentiment(coll, word="barnevern", return_score_only=False):
    """Compute a sentiment score of positive and negative terms in `coll`.

    The collocations of the `word` are used to count occurrences of positive and negative terms.

    :param coll: a collocations dataframe or a dh.Corpus where `word` occurs.
    :param str word: a word to estimate sentiment scores for
    :param bool return_score_only: If True,
        return a tuple with the absolute counts for positive and negative terms.
    """
    if isinstance(coll, dh.Corpus):
        coll = coll.coll(word).frame

    coll = group_index_terms(coll)

    # Data import
    data_dir = "../norsentlex/Fullform/"
    pos = pd.read_csv(data_dir + "/Fullform_Positive_lexicon.txt", names=["terms"])
    neg = pd.read_csv(data_dir + "/Fullform_Negative_lexicon.txt", names=["terms"])

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
