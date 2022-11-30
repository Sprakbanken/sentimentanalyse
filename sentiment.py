import pandas as pd
import dhlab as dh




def coll_sentiment(coll, word="barnevern", return_score_only=False):
    
    if isinstance(coll, dh.Corpus):
        coll = coll.coll(word).frame
        
        
    # Data import 
    pos = pd.read_csv("norsentlex/Fullform/Fullform_Positive_lexicon.txt", names=["terms"])
    neg = pd.read_csv("norsentlex/Fullform/Fullform_Negative_lexicon.txt", names=["terms"])
    
    
    def _count_sentiment_tokens(coll, terms):  
        target_terms = terms.join(coll, how="inner", on="terms")
        return target_terms    
    
    coll.index = coll.index.str.lower()
    coll.index.name = "index"
    coll = coll.groupby('index')["counts"].sum().to_frame("counts")
    
    assert coll.index.is_unique, "Collocation index is not unique..."

    positive_counts = _count_sentiment_tokens(coll, pos)
    negative_counts = _count_sentiment_tokens(coll, neg)
    
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


def sentiment_by_place(cities=["Kristiansand", "Stavanger"], from_year=1999, to_year=2010):


    
    for city in cities:
        lst = []
        for year in range(from_year, to_year):
            corpus = dh.Corpus(doctype="digavis", freetext=f"city: {city} year: {year}", limit=1000)
            pos, neg = coll_sentiment(corpus, "barnevern", return_score_only=True)
            
            lst.append(
                pd.DataFrame(
                    [[pos, neg, pos-neg]], 
                    index=[year], 
                    columns=["positive", "negative", "sum"]
                    )
                )
        
        yield pd.concat(lst)   