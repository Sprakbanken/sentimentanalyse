# sentimentanalyse
Utvikling av sentimentanalyse for DH-laben

## Sentimentanalyse på aviser med gitte nøkkelord

* fil: notebook [`sentiment_analysis_timeseries.ipynb`](sentiment_analysis_timeseries.ipynb)
* INNDATA: nøkkelord `word`
* PROSESS:
    - Hent aviskorpus fra 2000-2022 der en form av lemmaet til nøkkelordet forekommer.
    - Tell antall forekomster av nøkkelordet per URN.
    - Beregn sentimentscore for hver forekomst av nøkkelordet.
    - Plott et grafdiagram med sentimentscore over tid.
    - Legg til nb.no-URLer for hvert dokument i korpuset.
    - Formater filnavn og skriv til CSV-fil
* [UTDATA](#utdata): CSV-fil `sentimentanalyse_aviskorpus_<FRA ÅR>-<TIL ÅR>_<DAGENS DATO>.csv`, se [eksempel](sentimentanalyse_aviskorpus_2000-2022_2023-01-03.csv).

## Kildekode

* modulen [`sentiment.py`](sentiment.py) inneholder funksjonene som brukes i notebooken. Den innholder også hjelpefunksjoner som kan være nyttige i dhlab-pakken forøvrig.
* funksjon `count_and_score_target_words`:
* INNDATA: korpus (URN-liste) + nøkkelord
* PROSESS:
  * Hent konkordanser for nøkkelordet fra hver URN.
  * Tokeniser og tell forekomster av nøkkelordet per avis.
  * Last inn positive og negative termlister fra NorSentLex:
    - Github repo: [norsentlex](https://github.com/ltgoslo/norsentlex)
    - Råfiler: [Positive](https://raw.githubusercontent.com/ltgoslo/norsentlex/master/Fullform/Fullform_Positive_lexicon.txt) og [negative](https://raw.githubusercontent.com/ltgoslo/norsentlex/master/Fullform/Fullform_Negative_lexicon.txt) ord
    - Artikkel [Lexicon information in neural sentiment analysis:
    a multi-task learning approach](https://aclanthology.org/W19-6119) (Barnes et al., NoDaLiDa 2019)
  * Tell positive + negative ord i hver konkordanse rundt nøkkelordet og angi differansen som "sentimentscore".
* UTDATA: dataramme med informasjon som angitt i [tabellen](#utdata).

## Utdata

| Kolonne | Beskrivelse |
| --- | --- |
| dhlabid | DH-labens ID-nummer for det digitale tekstobjektet (OCR-scannet tekst) i databasene |
| urn | Unique Resource Name (digitalt bilde av tekstdokumentet, tilgjengelig i nettbiblioteket) |
| title |  Avistittel, navn på publikasjon |
| city  | Publiseringssted (oftest en by) |
| timestamp  | datostempel i ISO-format (YYYYMMDD) |
| year | årstall for publikasjonen |
| doctype | Dokumenttype (her er det bare aviser, "digavis") |
| word | nøkkelord i tekstutdragene (konkordansene) som sentimentanalysen ble utført på
| count | ordfrekvens: antall ganger nøkkelordet forekommer i den gitte avisutgivelsen |
| positive | antall positive ord i kontekstene nøkkelordet forekommer i |
| negative | antall negative ord i kontekstene |
| sentimentscore  | differansen positiv score - negativ score |
| url | lenke til avisen i nettbiblioteket, inkl. søk på nøkkelordet |


**FINT Å HA**:
- [ ] Hent geolokasjon/stedsnavn/landsdel for tittel på hver URN
- [ ] Lag en streamlit-app som kjører sentimentanalysen
