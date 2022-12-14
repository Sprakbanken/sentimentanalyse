# sentimentanalyse
Utvikling av sentimentanalyse for DH-laben


# sentimentanalyse på aviser med gitte nøkkelord

* INPUT: `nøkkelord`
* PROCESS:
    - [X] Hent aviskorpus fra 2000-2022 der en form av lemmaet til `nøkkelord` forekommer (iterativ prosess for å få tak i et så fullstendig korpus som mulig, 20 000 URNer av gangen)
    - [X] Hent ordfrekvens for `nøkkelord` fra hver URN i korpuset
    - [X] Kjør sentimentscore for hver URN + nøkkelord
    - [ ] (Fint å ha: Hent geolokasjon/stedsnavn/landsdel for tittel på hver URN )
    - [X] Formater utdata og skriv til CSV

* OUTPUT: CSV
  * [dato, avisnavn, `nøkkelord`, frekvens av `nøkkelord` i utgivelsen, sentimentscore]


## Sentimentscore
* INPUT: URN + nøkkelord
* PROCESS:
  * [X] Hent kollokasjons-df for URN, gitt `nøkkelord`
  * [X] Tell positive, negative ~~og nøytrale ord~~ i kollokasjons-BOW rundt `nøkkelord`
  * ~~[] normaliser resulterende sentiment-tall og returner en dict med scorene~~
* OUTPUT: `{"positiv": int, "negativ": int, "nøytral": int}`

**FINT Å HA**:
- [ ] Lag en streamlit-app som kjører sentimentanalysen

