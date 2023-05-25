import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
import dhlab as dh

from sentiment import compute_sentiment_analysis

## CONSTANTS ##
max_size_corpus = 20000
size_percent = 5  # percent of max_size_corpus
default_size = int(size_percent * max_size_corpus / 100)
today = datetime.date.today()
year = today.year
default_start_date = today.year - 50
default_word = "iskrem"


@st.cache_data
def header():
    st.markdown("""<style>
img{opacity: 1.0;}</style><a href="https://nb.no/dhlab">
<img src="https://raw.githubusercontent.com/NationalLibraryOfNorway/DHLAB-apps/main/sentiment-app/dhlab-logo-nb.png" style="width:250px"></a>""",
        unsafe_allow_html = True
    )
    st.title("Sentimentanalyse")
    st.write("Søk etter et nøkkelord, og få ut en graf over positive og negative ord som forekommer sammen med nøkkelordet.")


def v(x):
    """Turn empty string into None"""
    if x != "":
        res = x
    else:
        res = None
    return res


def define_params():
    params = {}
    slot1, slot2, slot3 = st.columns([3,2,1])
    with slot2:
        params["doctype"] = st.selectbox(
            "Type dokument",
            [
                "digibok",
                "digavis",
                "digitidsskrift",
                "digimanus",
                "digistorting",
                "kudos",
            ],
            help="Velg dokumenttype som skal inngå i korpuset. Valgmulighetene følger Nasjonalbibliotekets digitale dokumenttyper."
        )
        city= st.text_input(
            "Sted",
            "",
            placeholder="f.eks. Kristiansand, Molde, Bodø...",
            disabled=(params["doctype"] not in ['digavis', 'digibok']),
            help='Dersom dokumenttypen er "digavis" eller "digibok" kan du avgrense på publiseringssted.'
        )
        params["freetext"]= f"city: {city}" if city else None

    with slot1:
        params["word"] = st.text_input(
            "Nøkkelord",
            default_word,
            placeholder='f.eks. bibliotek, demokrati, fri*',
            help="Ord som skal forekomme i tekstutvalget."
        )
        params["title"] = st.text_input(
            "Tittel",
            "",
            help="Søk etter titler. For aviser vil tittel matche avisnavnet.",
            disabled=(params["doctype"] in ["digistorting"]),
        )
        params["author"] = st.text_input(
            "Forfatter",
            "",
            help='Feltet blir kun tatt hensyn til for "digibok"',
            disabled=(params["doctype"] != "digibok"),
        )


    with slot3:
        params["from_year"] = st.number_input('Fra år', min_value=1800, max_value=year, value=default_start_date)
        params["to_year"] = st.number_input('Til år', min_value=1800, max_value=year, value=year)
        params["limit"] = st.number_input(
            "Antall",
            min_value=1,
            max_value=max_size_corpus,
            value=default_size,
            help=f"Antall dokumenter som skal hentes ut. Maks {max_size_corpus}",
        )
    return params


@st.cache_data(persist=True, show_spinner=False)
def load_data(**params):
    """Instantiate a Corpus object."""
    df = dh.Corpus(
        doctype=v(params.get("doctype")),
        author=v(params.get("author")),
        fulltext=v(params.get("word")),
        freetext=v(params.get("freetext")),
        from_year=params.get("from_year", default_start_date),
        to_year=params.get("to_year", year),
        title=v(params.get("title")),
        limit=params.get("limit", default_size),
    ).frame
    return df


def corpus_selection():
    meta_tab, upload_tab = st.tabs(["Filtrer på metadata", "Last opp Excel-fil"])

    with meta_tab:
        with st.form(key='metadata_filter'):
            params = define_params()
            metadata_submitted = st.form_submit_button(label='Hent tekstutvalg')

        # raise a warning if file uploader has already loaded a corpus
        if st.session_state.get("file_uploader"):
            st.warning("Fjern det opplastede korpuset først.")

        if metadata_submitted:
            with st.spinner('Laster inn korpus...'):
                corpus = load_data(**params)
            st.write(f"Korpus lastet inn med {len(corpus)} dokumenter.")
            st.session_state.corpus = corpus

    with upload_tab:
        loaded_corpus = st.file_uploader(
                "Last opp korpusdefinisjon fra en Excel-fil", #"Last opp korpusdefinisjon fra ditt eget Excel-ark",
                type=["xlsx"],
                accept_multiple_files=False,
                key="file_uploader"
            )
        if st.session_state.file_uploader is not None:
            try:
                st.session_state.corpus = pd.read_excel(loaded_corpus)
            except:
                st.error("Opplasting feilet. Prøv igjen med en .xlsx-fil.")


@st.cache_data
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    processed_data = output.getvalue()
    return processed_data


def create_plot(result):
    """Plot the result scores."""
    r = result[["year","positive", "negative", "sentimentscore"]]
    rgroup = r.groupby("year")[["sentimentscore", "positive", "negative"]].sum()
    return rgroup.plot().figure

@st.cache_data
def sentiment_analysis(word):
    """Compute the sentiment analysis score."""
    if ("corpus" not in st.session_state):
        st.session_state.corpus = load_data(word=word, limit=50)
    try:
        result = compute_sentiment_analysis(st.session_state.corpus, word)
        figure = create_plot(result)
        st.pyplot(figure)
        st.session_state.result = True
        return result
    except Exception as error:
        st.write("Last inn et korpus og prøv igjen.")
        st.error(error)


if __name__ == "__main__":

    ## Page layout
    st.set_page_config(
        page_title="Sentiment",
        layout="wide",
        initial_sidebar_state="auto"
    )

    header()
    st.write("Flere apper fra [DH-laben](https://www.nb.no/dh-lab) finner du [her](https://www.nb.no/dh-lab/apper/).")

    st.subheader("Tekstutvalg")
    corpus_selection()

    st.session_state.result = False

    st.header("Analyser sentiment")
    with st.form(key='input_word'):
        word = st.text_input(
            "Sentimentord",
            default_word,
            placeholder='f.eks. sol, sommer, iskrem...',
            help=(
                "Ord som skal analyseres. "
                "Sentimentscoren regnes ut fra hvor mange av ordene i konteksten "
                "rundt sentimentordet som er positive eller negative. "
            ),
        )
        sentiment_button = st.form_submit_button(label = "Kjør!")
    if sentiment_button:
        result = sentiment_analysis(word)

    if "result" in st.session_state:
        st.write("---")
        filnavn = st.text_input("Filnavn for nedlasting", f"sentimentscore_{today}.xlsx")

        if st.download_button(
            'Last ned data i excelformat',
            to_excel(result),
            filnavn,
            help = "Åpnes i Excel eller tilsvarende regnearkprogram."
        ):
            pass

