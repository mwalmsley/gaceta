# gaceta

Scraping utility for downloading Gaceta parliamentary vote history.

## Install

Only needs `pandas`, `requests`, and `beautifulsoup4`.

    pip install -r requirements.txt

## Running

    python download_votes.py
    python parse_votes.py
    python join_votes.py

The server is quite unreliable - it seems to go through periods where any request returns a 404. The code is designed to stop if this happens. If you get errors like

    requests.exceptions.HTTPError: 404 Client Error: Not Found for url: http://gaceta.diputados.gob.mx/voto58/

then try again later.

Set `overwrite=True` in `download_votes.py` to always download every file, even if they already exist.

## Website file structure

Plain text files are hosted on the server with urls like

    http://gaceta.diputados.gob.mx/votoN/ordiXY/votoMMDD-I.txt

For example

    http://gaceta.diputados.gob.mx/voto64/voto64/ordi22/voto0630-1.txt

`votoN` is votes during the Nth parliament. For example, `voto64` is votes during the "LXIV Legislatura (2018-2021)", where LXIV=64 (took me way too long to notice).

`ordiXY` is the parliamentary year and period that year. [This page](http://gaceta.diputados.gob.mx/gp_votaciones.html) lists them in the form

- "first year (of the parliament), first ordinary period"
- "first year (of the parliament), second ordinary period"
- "first year (of the parliament), first extraordinary period"
- ...

so e.g. `ordi22` is the second year of the parliament, and the second ordinary session that year.

The text file name `votoMMDD-I.txt` is the date and the index of the proposal for that day. So e.g. `voto1219-2` is the second proposal of the day of Dec 19th.
