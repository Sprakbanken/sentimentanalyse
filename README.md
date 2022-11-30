# sentimentanalyse
Utvikling av sentimentanalyse for DH-laben


# sentimentanalyse på aviser med gitte nøkkelord

* INPUT: `nøkkelord`
* PROCESS:
    - [ ] Hent aviskorpus fra 2000-2022 der en form av lemmaet til `nøkkelord` forekommer (iterativ prosess for å få tak i et så fullstendig korpus som mulig, 20 000 URNer av gangen)
    - [ ] Hent ordfrekvens for `nøkkelord` fra hver URN i korpuset
    - [ ] Kjør sentimentscore for hver URN + nøkkelord
    - [ ] (Fint å ha: Hent geolokasjon/stedsnavn/landsdel for tittel på hver URN )
    - [ ] Formater utdata og skriv til CSV

* OUTPUT: CSV
  * [dato, avisnavn, ,  `nøkkelord`, frekvens av `nøkkelord` i utgivelsen, sentimentscore]


## Sentimentscore
* INPUT: URN + nøkkelord
* PROCESS:
  * [ ] Hent kollokasjons-df for URN, gitt `nøkkelord`
  * [ ] Tell positive, negative og nøytrale ord i kollokasjons-BOW rundt `nøkkelord`
  * [ ] normaliser resulterende sentiment-tall og returner en dict med scorene
* OUTPUT: `{"positiv": int, "negativ": int, "nøytral": int}`

**FINT Å HA**:
- [ ] Lag en streamlit-app som kjører sentimentanalysen

