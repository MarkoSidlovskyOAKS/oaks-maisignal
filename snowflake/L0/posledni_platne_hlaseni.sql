-- L0 raw table: SUKL posledni platne hlaseni (latest valid unavailability reports).
-- Source: https://opendata.sukl.cz/

CREATE TABLE IF NOT EXISTS maisignal.raw.posledni_platne_hlaseni (
    kod_sukl                    NUMBER       NOT NULL,
    nazev                       VARCHAR,
    doplnek                     VARCHAR,
    reg                         VARCHAR,
    atc                         VARCHAR,
    typ_oznameni                VARCHAR,
    platnost_od                 DATE,
    datum_hlaseni               DATE,
    nahrazujici_lp              VARCHAR,
    nahrazujici_lp_poznamka     VARCHAR,
    duvod_preruseni_ukonceni    VARCHAR,
    termin_obnoveni             DATE
);
