# Voynich-Manuskript: Was der Text statistisch zulässt und was nicht

Stand: 23. September 2026. Datenbasis: Zandbergen-Landini-Transkription ZL3b (EVA, IVTFF), nur Absatztext (Locus-Typ P), Wörter mit unsicheren Glyphen entfernt; unsichere Leerzeichen (`,`) als kein Leerzeichen behandelt, wo nicht anders angegeben. Referenztexte: Caesar (Latein), Faust (Deutsch), Dante (Italienisch), Tolstoi (Englisch), Genesis unvokalisiert (Hebräisch). Alle Zahlen stammen aus den Skripten in `scripts/`, die Werkzeuge aus `voynich/`.

## 0. Ergebnis in drei Sätzen

Der Text wurde nicht entziffert. Der belastbare Befund lautet: **Alle bisher getesteten beobachtbaren Strukturen sind mit einem lokalen, niedrigordentlichen Glyphengenerator vereinbar; weder lexikalische Struktur noch externe bildbezogene Semantik ist darüber hinaus messbar.** Voynichesisch benötigt in diesen Messungen keine Wort-, Satz- oder andere höherstufige Struktur, um erklärt zu werden; ein lokaler Glyphenprozess niedriger Ordnung mit Zeilenreset und lokaler Parameterdrift reicht aus. "Nicht messbar" ist quantifiziert: Eine Beschreibung, bei der etwa 13 % oder mehr der Wörter systematisch von den gemessenen Bildmerkmalen abhängen, hätte der Test mit hoher Wahrscheinlichkeit erkannt (3.8). Zwei Einschränkungen bleiben: Die Farbmerkmale sind nur ein grober Proxy für Bedeutung, und ein Text könnte Pflanzennamen, Anwendungen oder Eigenschaften beschreiben, die im Bild nicht sichtbar sind. Der Befund sagt deshalb nicht, dass der Text bedeutungslos ist. Der stärkste Teil des Befundes ist die Kombination aus zwei Transkriptionen, mehreren Schreiberhänden, beiden Currier-Sprachen und echter Out-of-sample-Prüfung: Ein auf ungeraden Folios angepasstes Modell niedriger Ordnung generalisiert auf ungesehene Folios und reproduziert dort die entscheidenden Statistiken (4.1). Hypothesen und Kennzahlen sind mit diesem Stand eingefroren; weitere Arbeit sollte der unabhängigen Reproduktion gelten, nicht neuen Maßen. Im Einzelnen: Die Voynich-"Wörter" sind keine lexikalischen Einheiten, die Leerzeichen keine Wortgrenzen, und die gesamte messbare Ordnungsinformation sitzt an den Glyphenübergängen, nicht in Wortidentitäten oder Wortfolgen. Ein sehr einfacher lokaler Glyphenprozess (Automat dritter bis vierter Ordnung, Parameter driften von Seite zu Seite, Neustart an jedem Zeilenanfang) reicht aus, um jede gemessene Statistik des Textes innerhalb des Rauschens zu reproduzieren. Das beweist nicht, dass der Text so erzeugt wurde; es heißt, dass nach Kenntnis der lokalen Übergangsregeln kaum zusätzliche Struktur im Text übrig bleibt. Jeder Mechanismus, der einen Klartext in natürlicher Sprache voraussetzt (einfache, homophone, verbose oder rückgekoppelte Substitution) oder der ganze Wörter erzeugt (Rugg-Tabelle, Timm/Schinner-Kopieren), verfehlt mindestens zwei der Kennzahlen deutlich.

## 1. Grundstatistik

| Korpus | Tokens | Typen | TTR | Hapax | Wortlänge | h1 | h2 | Zipf |
|---|---|---|---|---|---|---|---|---|
| Voynich (Absatztext) | 34 886 | 6 875 | 0,197 | 0,67 | 4,96 | 3,87 | 2,10 | −0,78 |
| Currier A | 11 246 | 3 140 | 0,279 | 0,68 | 4,75 | 3,83 | 2,14 | −0,79 |
| Currier B | 23 091 | 4 724 | 0,205 | 0,68 | 5,07 | 3,87 | 1,99 | −0,81 |
| Latein (Caesar) | 34 886 | 8 426 | 0,242 | 0,59 | 6,10 | 4,02 | 3,30 | −0,75 |
| Deutsch (Faust) | 30 959 | 6 221 | 0,201 | 0,63 | 4,78 | 4,13 | 3,19 | −0,95 |
| Italienisch (Dante) | 34 886 | 6 574 | 0,188 | 0,62 | 3,92 | 4,01 | 3,15 | −0,94 |
| Hebräisch (Genesis) | 17 789 | 6 319 | 0,355 | 0,65 | 4,41 | 4,13 | 3,53 | −0,65 |

h1 = Unigramm-Entropie, h2 = bedingte Bigramm-Entropie pro Glyphe (mit Leerzeichen). Die Wortebene sieht sprachähnlich aus (10,2 Bit pro Wort gegenüber 9,8 bis 11,0 in den Referenzen). Die Glyphenebene nicht: h2/h1 = 0,54 gegenüber 0,77 bis 0,85. Die Wortlängenverteilung ist eng (Maximum bei 5, praktisch nichts über 9).

## 2. Was ausgeschlossen werden konnte

### 2.1 Einfache oder homophone Substitution

Ein Hill-Climbing-Löser mit 4-Gramm-Sprachmodell (`voynich/subst.py`) knackt eine homophone Chiffre mit 49 Einheiten über lateinischem Text vollständig (Einheiten-Genauigkeit 1,00) und erreicht dort 2,45 Bit pro Zeichen, den Wert des Klartexts. Auf dem Voynich-Text erreicht er 3,17 Bit, auf Zufallstext mit denselben Einheitenhäufigkeiten 3,86. Auf dem Voynich-Text mit zufällig vertauschten Wörtern erreicht er 3,20: fast der gesamte "Sprachanteil", den der Löser findet, stammt aus der Wortinnenstruktur, nicht aus der Wortfolge.

### 2.2 Verbose-Chiffre und Silbenhypothese

Wendet man auf Voynich und auf die Referenzsprachen dieselbe BPE-Merge-Folge an, bleibt h2/h1 bei allen Sprachen invariant bei 0,75 bis 0,85. Voynich startet bei 0,54 und erreicht nach 80 Merges (105 Einheiten, zwei Einheiten pro Wort) erst 0,74. Keine Segmentierung in ein Alphabet plausibler Größe macht den Glyphenstrom sprachähnlich. Lateinische Silben (1 124 Typen, TTR 0,03) und Silbenpaare (13 538 Typen, TTR 0,39) passen ebenfalls nicht zum Voynich-Wortinventar.

### 2.3 Abschreiben aus der Vorzeile

Das Wort direkt darüber ist einem Wort nicht ähnlicher als ein zufälliges Wort derselben Seite: P(Editierdistanz ≤ 1) 0,044 gegen 0,038; Minimum über drei Kandidaten darüber 0,108 gegen Minimum über drei zufällige Seitenwörter 0,109. Die zunächst gefundene Nachbarähnlichkeit ist vollständig Seitenlokalität des Vokabulars (gleiche Seite 0,038, gleiche Sprache 0,025).

### 2.4 Kein Lexikon

Trainiert man ein Glyphen-Trigramm-Modell auf der Hälfte der Tokens und zieht daraus zufällige Wörter, sind diese im Trainingsteil genauso oft belegt wie echte zurückgehaltene Wörter:

| Korpus | echte Tokens belegt | synthetische Tokens belegt | echte Typen | synthetische Typen |
|---|---|---|---|---|
| Voynich | 0,79 | 0,76 | 0,36 | 0,30 |
| Latein | 0,80 | 0,20 | 0,48 | 0,03 |
| Deutsch | 0,83 | 0,34 | 0,44 | 0,07 |
| Italienisch | 0,84 | 0,52 | 0,44 | 0,09 |
| Latein, Regel-Leerzeichen | 0,62 | 0,28 | 0,28 | 0,09 |
| Latein, Silbenpaare | 0,65 | 0,09 | 0,42 | 0,09 |

Jede Sprache und jede Zerhackung einer Sprache behält eine Lexikonlücke. Der Voynich-Text hat keine: Ein "Wort" ist genau das, was der Glyphenautomat ausgibt.

## 3. Die Struktur, die tatsächlich da ist

### 3.1 Information sitzt an der Glyphengrenze

Überschuss an Mutual Information benachbarter Wörter innerhalb einer Zeile (Randwörter ausgeschlossen, Nullmodell: Permutation innerhalb der Zeile, Marginalien erhalten):

| Projektion | Voynich | Currier B | Latein | Deutsch | Hebräisch |
|---|---|---|---|---|---|
| Wort → Wort | 0,076 | 0,081 | 0,242 | 0,216 | 0,178 |
| letzte Glyphe → erste Glyphe | 0,146 | 0,187 | 0,037 | 0,056 | 0,047 |
| letzte zwei → erste zwei | 0,184 | 0,227 | 0,212 | 0,173 | 0,332 |

Die Hierarchie ist gegenüber allen Sprachen umgekehrt. Die überrepräsentierten Nachbarpaare sind Grenzregeln ("-y" vor "qo-", "-l/-r/-s" vor "a-" oder "ch-/sh-"), nicht Kollokationen verschiedener Wörter. Zerlegt man die Nachbar-MI nach Editierdistanz, liegt in den Sprachen fast alles in unähnlichen Paaren (Latein 0,24 von 0,26 Bit bei ED ≥ 3); im Voynich-Text liegt sie vollständig in Paaren mit ED ≤ 2.

Wortgrenzen sind aus dem flankierenden Glyphenpaar vorhersagbar: Informationsgewinn 74 % (F1 0,85) gegenüber 39 bis 45 % in vier Sprachen. Entfernt man in Latein die Leerzeichen und fügt sie nach einer Glyphenregel wieder ein, ergibt sich exakt das Voynich-Profil (73 %, F1 0,84).

### 3.2 Die Zeile ist ein Neustart

Von allen Wortpaaren zwischen aufeinanderfolgenden Zeilen trägt in Latein und Italienisch nur das Paar (letztes Wort, erstes Wort) Information (0,065 bzw. 0,178), weil der Text weiterläuft. Im Voynich-Text ist dieses Paar das informationsärmste von allen (0,003), unter dem Seitenboden von 0,01 bis 0,02, den beliebige Wortpaare derselben Seite haben. Mit identisch geschnittenen Zeilen und Absätzen: Voynich über den Umbruch 0,005 gegen 0,062 bei gleicher Stichprobengröße innerhalb der Zeile; Latein 0,077 gegen 0,070, Italienisch 0,166 gegen 0,171, Deutsch 0,055 gegen 0,060. Das letzte Wort jeder Zeile ist zudem das seitenunabhängigste (I(Wort; Seite) 0,055 gegen 0,113 in der Zeilenmitte) und vielfältigste Wort der Zeile.

### 3.3 Keine Kongruenz, keine Richtung

Nachbarwörter teilen Endungen und Anfänge exakt so oft wie zufällig angeordnete Wörter derselben Zeile (Quotienten 0,94 bis 1,04 für erste, erste zwei, letzte, letzte zwei, letzte drei Glyphen und Identität). Latein und Italienisch zeigen Kongruenz (gleiche Endglyphe 1,10 und 1,16) und vermeiden identische Nachbarn (0,00 bis 0,24). Die berühmten Wiederholungen ("qokeedy qokeedy") treten mit der Zufallsrate auf. Einzelglyphen-Änderungen zwischen Nachbarn (739 Paare) sind nicht gerichtet: "q" wird 37-mal hinzugefügt und 35-mal entfernt, k↔t 27 gegen 24, kein z-Wert über 1,8.

### 3.4 Das Entropieprofil ist das eines Automaten

Bedingte Entropie pro Glyphe bei wachsendem Kontext, verglichen mit synthetischen Zwillingen, die aus dem angepassten Modell mit denselben Zeilenlängen gezogen wurden:

| Text | h(1) | h(2) | h(3) | h(4) | h(5) | Differenz zum Ordnung-3-Zwilling bei h(3)..h(5) |
|---|---|---|---|---|---|---|
| Voynich | 1,91 | 1,82 | 1,72 | 1,57 | | −0,03 / −0,06 / −0,06 |
| Latein | 2,72 | 2,11 | 1,66 | 1,33 | | 0,00 / −0,29 / −0,30 |
| Italienisch | 2,77 | 2,31 | 1,88 | 1,43 | | +0,02 / −0,18 / −0,18 |
| Deutsch | 2,63 | 2,10 | 1,71 | 1,38 | | +0,01 / −0,18 / −0,17 |
| Hebräisch | 2,90 | 2,22 | 1,60 | 1,05 | | +0,09 / −0,13 / −0,15 |

(h(k) = Entropie gegeben k vorangehende Symbole, Leerzeichen als Symbol.) Mit Sektionsdrift im Zwilling fällt auch die lzma-Differenz des Voynich-Textes auf −0,04 Bit pro Glyphe (Rauschboden ±0,03), gegenüber −0,34 bis −0,53 bei den Sprachen.

### 3.5 Die Parameter driften mit dem Folio-Abstand

Jensen-Shannon-Divergenz der Glyphen-Bigrammverteilungen zwischen Seiten derselben Currier-Sprache, nach Folio-Abstand:

| | d = 1–2 | 3–6 | 7–14 | 15–40 | > 40 | andere Sektion |
|---|---|---|---|---|---|---|
| Voynich A | 0,124 | 0,145 | 0,150 | 0,150 | 0,161 | 0,193 |
| Voynich B | 0,126 | 0,137 | 0,134 | 0,147 | 0,147 | 0,169 |
| Automat mit Sektionsdrift | 0,093 | 0,094 | 0,094 | 0,094 | 0,094 | 0,149 |
| Latein in Buchreihenfolge | 0,183 | 0,188 | 0,195 | 0,192 | 0,192 | 0,193 |

Der Voynich-Text hat beides: seitenspezifische Abweichung (0,124 gegen 0,093 beim Zwilling schon bei d = 1–2) und einen glatten Anstieg mit dem Abstand, den lateinische Prosa auf Buchstabenebene nicht zeigt. Das ist die Signatur eines zeitartigen Prozesses (Schreibgewohnheit), nicht eines themengebundenen.

### 3.6 Die Parameter folgen der Schreiberhand

Die ZL-Metadaten enthalten die paläographische Händezuweisung ($H, fünf Schreiber nach Lisa Fagin Davis), die unabhängig von Statistik aus den Buchstabenformen gewonnen wurde. Innerhalb der Sektion Herbal-B (32 Seiten, Hände 2, 3 und 5) bei Folio-Abstand ≤ 6: Jensen-Shannon-Divergenz der Glyphen-Bigramme zwischen Seiten derselben Hand 0,138, zwischen Seiten verschiedener Hände 0,182. Der Handeffekt bei festem Abstand und fester Sektion (+0,044) ist größer als der Sektionseffekt bei fester Hand (+0,037, mit dem Folio-Abstand konfundiert). Die Bigramme, in denen sich Hand 2 und Hand 3 in derselben Sektion unterscheiden (Hand 2: "edy", "ke", "he", "dy"; Hand 3: "aiin", "ot", "ka", "ta"), sind genau die Achse, die Currier A von B trennt. Die beobachtete Variation folgt der Schreiberhand stärker als der inhaltlichen Sektion; damit ist Schreiberpraxis eine plausible Quelle der Parameterdrift. Dass Hände und statistische Profile zusammenfallen, ist nicht neu: Currier (1976) hat es bemerkt, und Davis berichtet, dass Schreiber 1 Currier A und Schreiber 2 Currier B entspricht, während die Schreiber 3 bis 5 überwiegend B verwenden. Neu ist hier nur der kontrollierte Vergleich: bei gleicher Sektion, gleicher Currier-Sprache und festem Folio-Abstand ist der Handeffekt größer als der Sektionseffekt bei fester Hand. Eine Chiffre schließt das nicht aus, weil ein Schreiber bei derselben Chiffre eigene Tafelwahl, Abkürzungen, Varianten oder Fehler haben kann.

### 3.7 Labels sind ein eigenes System

Labels (Locus-Typen L und &L, 1 029 Tokens nach Korrektur des Parsers) kehren über die Seiten einer Sektion hinweg seltener wieder als zufällig gezogene Textwörter derselben Seiten:

| Sektion | Seiten | Label-Tokens | Typen | Wiederkehr über Seiten | Nullmodell (Textwörter) |
|---|---|---|---|---|---|
| Zodiak | 12 | 330 | 271 | 0,276 | 0,363 |
| Astronomie | 5 | 142 | 136 | 0,028 | 0,273 |
| Pharma | 15 | 234 | 219 | 0,090 | 0,364 |
| Biologie | 11 | 122 | 111 | 0,115 | 0,342 |
| Kosmologie | 5 | 196 | 181 | 0,020 | 0,277 |

Wären die Zodiak-Labels Tages- oder Gradzahlen, müssten sie über die zwölf Zeichen fast vollständig wiederkehren; nur 25 Typen stehen auf zwei oder mehr Zeichenseiten (maximal vier: "otaly", "otal", "oky", "okeey"). Labels verhalten sich wie eindeutige Kennungen, weder wie Zahlen noch wie Textwörter, und beginnen zu 53 % mit "o" (Text: 20 %). Ob das Namen sind oder Automatenausgabe mit Wiederholungsvermeidung, entscheiden diese Daten nicht.

### 3.8 Trägt der Text Information über etwas außerhalb des Textes?

Das ist der entscheidende Test gegen die Hypothese "Pseudotext": Kann man aus dem Text einer Seite vorhersagen, was auf ihr abgebildet ist, nachdem Schreiberhand und Folio-Position kontrolliert sind? Als externe Variable dienen Farbmerkmale der Illustrationen, direkt aus dem Beinecke-Scan berechnet (PDF-Seiten 3 bis 116 = f1r bis f58v, f12 fehlt; Klassifikation relativ zum Pergamentton jeder Seite: Grün-, Blau-, Rot/Braun-Anteil, Schwerpunkte, Grünton, Farbverhältnisse; `scripts/scripts_page_colors.py`). Diese Merkmale sind nicht nach Folio geordnet (Bild gegen Folio-Abstand r = +0,07). Getestet wird mit einem Mantel-Test über Seitenpaare: Spearman-Korrelation zwischen Textabstand (Hellinger-Abstand der Wortverteilungen bzw. der Glyphen-Bigrammverteilungen) und Bildabstand (euklidisch im standardisierten Merkmalsraum), Permutations-Null über die Seitenidentität der Bilder, Paare mit Folio-Abstand unter 3 Folios ausgeschlossen.

| Teilmenge | Textebene | r | p | Text gegen Folio-Abstand |
|---|---|---|---|---|
| Herbal-A, Hand 1, 85 Seiten, 3 237 Paare | Wörter | −0,055 | 0,79 (10 000 Permutationen) | +0,115 (p = 0,001) |
| Herbal-A, Hand 1 | Glyphen-Bigramme | −0,070 | 0,87 | +0,032 (p = 0,18) |
| Herbal-B, Hände 2 und 5, 25 Seiten, Permutation innerhalb der Hand | Wörter | +0,223 | 0,076 | +0,163 (p = 0,04) |
| Herbal-B, nur Paare derselben Hand | Wörter | +0,144 | 0,14 | |
| Herbal-B, nur Hand 2, 20 Seiten | Wörter | +0,143 | 0,14 | |
| Herbal-B, nur Hand 2 | Glyphen-Bigramme | −0,036 | 0,58 | |

In Herbal-A gibt es keine Korrelation, auch nicht für ein einzelnes Bildmerkmal (alle p ≥ 0,22), während dieselbe Wortähnlichkeit die Folio-Drift klar zeigt. Der schwache Wert in Herbal-B (p = 0,046 ohne Stratifizierung) verschwindet, sobald die Permutation innerhalb der Hand erfolgt oder nur Hand 2 betrachtet wird; er lief über die Hand (Malstil und Schreiber sind beide an die Lage gebunden).

Empfindlichkeit (synthetische Positivkontrolle in Herbal-A): Fügt man jeder Seite k aus ihren Bildmerkmalen abgeleitete "Beschreibungswörter" hinzu (durchschnittlich 77 Wörter pro Seite), wird der Test bei k = 10 signifikant (r = +0,195, p = 0,001), bei k = 20 stark (r = +0,366), bei k = 5 noch nicht (r = +0,05, p = 0,21). Der Nullbefund schließt also aus, dass mindestens etwa 13 % der Wörter einer Herbal-A-Seite durch die hier gemessenen Bildmerkmale bestimmt sind; feinere Inhalte (Pflanzenidentität, Heilwirkung) oder Beschreibungen unter 5 Wörtern pro Seite sieht der Test nicht.

Sekundär, mit Vorbehalt: Die Vorhersage der Sektion innerhalb einer Hand ist mit der Folio-Position konfundiert, weil Sektionen zusammenhängende Folio-Bereiche sind. Leave-one-out mit Nächster-Zentroid-Klassifikation, Folio-Nachbarn ausgeschlossen: In Hand 1 (Herbal gegen Pharma, 95 gegen 16 Seiten) erreichen Wörter 0,79 bis 0,81 und Bigramme 0,75 bis 0,80, beides unter der Mehrheitsrate 0,86. In Hand 2 (Biologie gegen Herbal-B, 19 gegen 20 Seiten) erreichen Glyphen-Bigramme 0,79 bis 0,95, Wörter nur 0,42 bis 0,74, die Folio-Position allein 0,49 bis 1,00. In Hand 3 (Sterne gegen Herbal-B) liegen Wörter bei der Mehrheitsrate. Wo überhaupt Sektionsinformation im Text steckt, steckt sie in den Parametern des lokalen Glyphenprozesses, nicht in Wortidentitäten darüber hinaus, und sie ist von Drift nicht zu trennen.

## 4. Mechanismus-Batterie

Alle Generatoren erzeugen Text in exakt der Zeilen- und Wortform des Manuskripts (`voynich/generators.py`); die Batterie (`voynich/battery.py`) misst dieselben Größen auf allen. "Residuum" = lzma-Bitrate des Textes minus die eines an denselben Text angepassten Ordnung-3-Automaten mit Sektionsdrift, also Redundanz jenseits des Automaten.

| Mechanismus | Edge-MI | Token-MI | Zeilenumbruch-MI | Space-Gain | Hapax | Zipf | Lexikon real / synth | Residuum | I(Wort;Seite) |
|---|---|---|---|---|---|---|---|---|---|
| **Voynich** | 0,146 | 0,078 | 0,005 | 73,7 % | 0,71 | −0,75 | 0,79 / 0,75 | −0,039 | 0,232 |
| Automat Ordnung 3, Sektionsdrift | 0,167 | 0,050 | 0,005 | 73,8 % | 0,71 | −0,77 | 0,79 / 0,76 | +0,033 | 0,134 |
| Automat Ordnung 4, Sektionsdrift | 0,149 | 0,069 | −0,001 | 74,1 % | 0,64 | −0,74 | 0,81 / 0,76 | −0,030 | 0,138 |
| **Automat Ordnung 4, Seitendrift (λ = 0,5)** | 0,154 | 0,070 | 0,010 | 73,5 % | 0,64 | −0,74 | 0,81 / 0,76 | −0,041 | 0,212 |
| Latein, echte Wörter | 0,034 | 0,245 | 0,076 | 38,9 % | 0,59 | −0,76 | 0,80 / 0,20 | −0,397 | 0,062 |
| Latein, Regel-Leerzeichen | 0,134 | 0,198 | 0,067 | 72,8 % | 0,77 | −0,55 | 0,62 / 0,29 | −0,429 | 0,043 |
| Rugg-Tabelle mit Gitter | 0,006 | 0,613 | 0,041 | 62,8 % | 0,41 | −0,51 | 0,73 / 0,55 | −0,766 | 0,049 |
| Timm/Schinner-Kopieren | 0,010 | 0,022 | 0,042 | 46,7 % | 0,62 | −0,41 | 0,57 / 0,23 | −1,030 | 0,912 |
| Verbose-Chiffre, unabhängige Zeilen | 0,409 | 1,237 | 0,136 | 47,4 % | 0,30 | −0,77 | 0,93 / 0,64 | −0,950 | 0,015 |
| Chiffrat-Rückkopplung (stateful substitution), 1 Glyphe/Buchstabe | 0,649 | 0,160 | 0,006 | 36,5 % | 0,78 | −0,41 | 0,39 / 0,27 | −0,310 | 0,003 |
| Chiffrat-Rückkopplung, 2 Glyphen/Buchstabe | 0,615 | 0,305 | 0,009 | 38,6 % | 0,70 | −0,49 | 0,54 / 0,32 | −0,424 | 0,007 |
| **Naibbe-Chiffre** (Greshko 2025), Latein, unabhängige Zeilen | 0,003 | 0,055 | 0,002 | 77,4 % | 0,49 | −1,00 | 0,85 / 0,72 | −0,065 | 0,007 |
| Naibbe, Latein, Fließtext | 0,002 | 0,078 | 0,023 | 77,0 % | 0,49 | −1,01 | 0,84 / 0,72 | −0,050 | −0,007 |
| Naibbe, Italienisch, Fließtext | 0,002 | 0,066 | 0,029 | 76,8 % | 0,47 | −1,01 | 0,86 / 0,69 | −0,065 | 0,001 |
| Naibbe zustandsabhängig (Tafelwahl nach voriger Glyphe, w = 0,6) | 0,039 | 0,111 | 0,003 | 76,7 % | 0,48 | −1,02 | 0,85 / 0,68 | −0,101 | −0,007 |
| Naibbe zustandsabhängig, w = 0,9 | 0,085 | 0,181 | −0,001 | 76,7 % | 0,48 | −1,01 | 0,86 / 0,64 | −0,148 | 0,004 |
| Naibbe zustandsabhängig, w = 1,0 | 0,255 | 0,342 | 0,001 | 75,4 % | 0,49 | −0,99 | 0,87 / 0,66 | −0,222 | 0,002 |

Die Naibbe-Chiffre (verbose homophone Substitution mit sechs Tafeln, Tafelwahl per Kartenziehung, Wörter aus Unigramm-Strings oder Präfix+Suffix, aus den publizierten Tafeln nachgebaut in `voynich/generators.py`) ist der stärkste Gegner: Sie trifft Entropieprofil (h(2) 1,90, h(4) 1,70), Token-MI, Space-Gain, Wortlänge und, anders als alle anderen Klartext-Mechanismen, auch das Kompressionsresiduum, weil die Zufallsentropie der Kartenziehungen die Klartextredundanz überdeckt. Sie scheitert um Faktor 50 an der Edge-Kopplung (0,003 gegen 0,146), am Hapax-Anteil (0,49 gegen 0,71), am Zipf-Exponenten (−1,00 gegen −0,75) und an der Seitenlokalität (0,007 gegen 0,232). Der Lexikontest trennt sie nur schwach (Lücke 0,13 gegen 0,04): Konkatenationen von Tafelstrings sehen für ein Glyphen-Trigramm-Modell fast wie ein offenes Inventar aus.

Macht man die Tafelwahl von der letzten Glyphe des vorigen Wortes abhängig (Anteil w der Ziehungen zustandsabhängig statt zufällig), entsteht Edge-Kopplung, aber sie wird mit Schlüsselentropie bezahlt: Bei w = 1,0 liegt die Edge-MI mit 0,255 über dem Manuskript, gleichzeitig steigt die Token-MI auf 0,342 (Manuskript 0,078) und das Residuum auf −0,222 (Manuskript −0,039), weil die Klartextstruktur durchscheint. Bei w = 0,9 ist die Edge-MI mit 0,085 noch zu klein, die Token-MI mit 0,181 schon zu groß. Kein Wert von w trifft beide Größen; der Hapax-Anteil bleibt bei 0,48. Für eine Chiffre stehen Edge-Kopplung und verborgene Klartextredundanz in Konkurrenz; für einen Automaten ohne Klartext nicht.

Der Automat mit Seitendrift trifft jede Spalte innerhalb des Rauschens; einziger Rest ist der Hapax-Anteil (0,64 gegen 0,71), den die Ordnung-3-Variante trifft, die dafür weniger Token-MI hat. Kein generierter Zeilentext ist eine Kopie einer echten Zeile (0 von 4 100). Automaten der Ordnung 5 und 6 überschießen die Token-MI und beginnen zu memorieren. Wortbasierte Generatoren (Rugg, Timm/Schinner) verfehlen die Edge-Kopplung um mehr als eine Größenordnung; sprachbasierte Chiffren verfehlen Lexikontest, Hapax-Anteil, Space-Vorhersagbarkeit und lassen 0,3 bis 1,0 Bit pro Glyphe Redundanz jenseits des Automaten zurück.

### 4.1 Robustheit: Transkription, Out-of-sample, Hände, Sprachen

| Teilmenge | Edge-MI | Token-MI | Umbruch-MI | Space-Gain | Hapax | Lexikon real / synth | h(2) | h(4) | Residuum | I(Wort;Seite) |
|---|---|---|---|---|---|---|---|---|---|---|
| ZL3b (Basis) | 0,146 | 0,078 | 0,005 | 73,7 % | 0,71 | 0,79 / 0,75 | 1,91 | 1,72 | −0,039 | 0,232 |
| Takahashi IT2a | 0,165 | 0,116 | 0,011 | 75,2 % | 0,68 | 0,83 / 0,79 | 1,89 | 1,71 | −0,039 | 0,245 |
| gerade Seiten (held-out) | 0,150 | 0,034 | −0,001 | 74,1 % | 0,71 | 0,75 / 0,73 | 1,89 | 1,66 | | 0,289 |
| Zwilling aus Modell der ungeraden Seiten | 0,150 | 0,007 | 0,000 | 73,8 % | 0,71 | 0,74 / 0,73 | 1,92 | 1,70 | | 0,168 |
| Hand 1 (112 Seiten) | 0,079 | 0,060 | 0,001 | 70,5 % | 0,71 | 0,71 / 0,71 | 1,93 | 1,65 | | 0,129 |
| Hand 2 (46 Seiten) | 0,195 | 0,087 | −0,001 | 77,4 % | 0,70 | 0,78 / 0,74 | 1,72 | 1,50 | | 0,237 |
| Hand 3 (31 Seiten) | 0,185 | 0,041 | 0,006 | 74,8 % | 0,72 | 0,71 / 0,69 | 1,79 | 1,56 | | 0,182 |
| Currier A | 0,082 | 0,049 | 0,007 | 70,6 % | 0,72 | 0,71 / 0,72 | 1,95 | 1,68 | | 0,131 |
| Currier B | 0,187 | 0,081 | 0,007 | 76,8 % | 0,71 | 0,78 / 0,76 | 1,78 | 1,60 | | 0,224 |

Out-of-sample (Automat auf den ungeraden Seiten angepasst, auf den geraden ausgewertet): lzma-Residuum −0,030 (Ordnung 3), +0,020 (Ordnung 4), umgekehrte Teilung +0,010; h(3)-Residuum −0,012 bis +0,038. Alles innerhalb des Rauschbodens. Die zurückgehaltenen echten Seiten und der aus dem Trainingsmodell gezogene Zwilling stimmen in Edge-MI (0,150 / 0,150), Space-Gain, Hapax, Zipf, Lexikon und Entropieprofil überein; die Differenz in Token-MI (0,034 / 0,007) und Seitenlokalität (0,289 / 0,168) ist der Seitendrift, die ein Modell auf Sektionsebene nicht enthält (vgl. Automat mit Seitendrift in der Haupttabelle). Der Befund gilt für beide Transkriptionen, für jede Hand und für beide Currier-Sprachen; die Edge-Kopplung ist in Hand 1 / Sprache A schwächer (0,08) als in den Händen 2 und 3 / Sprache B (0,19), die Lexikonlücke ist überall ≤ 0,04.

## 5. Was daraus folgt

1. **Jede getestete Kodierung eines natürlichsprachlichen Klartexts scheitert, aber nicht alle am selben Maß.** Deterministische Chiffren (einfach, verbose mit fester Homophonwahl, Chiffrat-Rückkopplung) hinterlassen Lexikon, unvorhersagbare Wortgrenzen und mindestens 0,3 Bit pro Glyphe Redundanz jenseits des Automaten. Eine homophone Chiffre mit hoher Schlüsselentropie wie Naibbe überdeckt Lexikon und Redundanz fast vollständig; sie scheitert an der Edge-Kopplung, am Hapax-Anteil, am Zipf-Exponenten und an der Seitenlokalität. Die Edge-Kopplung ist das einzige Maß, an dem **alle** Klartext- und alle wortbasierten Mechanismen zugleich scheitern (Faktor 15 bis 50).
2. **Wortbasierte Erzeugung ist ausgeschlossen.** Alles, was Wörter als Einheiten erzeugt oder kopiert, hat keine Kopplung über die Wortgrenze; der Text hat 0,15 bis 0,19 Bit davon.
3. **Ein anderer Prozess mit demselben statistischen Fußabdruck ist nicht ausgeschlossen; der Automat ist ein positives Nullmodell, kein Erzeugungsnachweis.** Was ein solcher Prozess leisten müsste, steht in Punkt 4.
4. **Übrig bleiben zwei Klassen.** Erstens ein bedeutungsloser Erzeugungsprozess niedriger Ordnung, dessen Übergangsparameter mit einem menschlichen Schreiber driften (die Drift mit dem Folio-Abstand spricht für einen zeitlichen, nicht thematischen Prozess). Zweitens eine Kodierung von Inhalt, der selbst praktisch inkompressibel ist (Zahlenkolonnen, Schlüssel, bereits komprimierte Daten). Für die zweite Klasse gibt es keinen positiven Hinweis: Geordnete Tabellen würden vertikale Struktur erzeugen, und die fehlt (2.3); Listeneinträge mit fester Form würden stärkere Positionsabhängigkeit zeigen als gemessen (I(Wort; Position) 0,09 bis 0,12 gegenüber 0,23 bei Dante-Versen).
5. **Drei mögliche Endspiele, und wo dieser Befund steht.** (a) Entzifferung: eine Transformation, die auf ungesehenen Folios sinnvollen Klartext liefert und Labels oder Bilder erklärt; nicht erreicht, und nichts hier deutet auf einen Weg dorthin. (b) Generator identifiziert: ein konkreter, historisch plausibler Mechanismus, der ungesehenen Text so gut vorhersagt wie das Manuskript selbst; der Automat leistet das statistisch, ist aber kein historisches Verfahren, sondern ein Nullmodell. (c) Keine nachweisbare Semantik: nach Kontrolle von Hand, Sektion und Folio lässt sich aus dem Text nichts Externes vorhersagen, und ein lokaler Automat erreicht auf zurückgehaltenen Folios praktisch die gesamte erreichbare Vorhersageleistung. **Hier steht der Befund**, mit quantifizierter Empfindlichkeit (3.8): Wir finden keine Information im Text, die über den lokalen Erzeugungsprozess hinausgeht. Das ist kein Beweis von Bedeutungslosigkeit; eine Kodierung, die genau diese Information unter die Empfindlichkeitsgrenze drückt, bleibt logisch möglich.
6. **Was eine Chiffre leisten müsste, ist damit scharf umrissen:** zustandsabhängige Wahl der Glyphenstrings (für die Edge-Kopplung von 0,15 Bit über die Wortgrenze), hohe Schlüsselentropie (damit Klartextredundanz und Lexikon verschwinden), ein offenes Inventar von Tausenden Strings (Hapax 0,71 bei 32 000 Tokens), keine Fortsetzung über Zeilenumbrüche, und Parameter, die mit der Folio-Reihenfolge driften. Ein solches Verfahren wäre per Konstruktion ein driftender Glyphenautomat, dessen Zustandsübergänge vom Klartext mitgesteuert werden. Keine publizierte Chiffre hat diese Eigenschaften; ob sie historisch plausibel wäre, ist eine andere Frage als ob sie statistisch möglich ist.

## 6. Einordnung in die Literatur

Rozanova & Temerev, "A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space" (arXiv 2608.17096, 17. August 2026), kommen auf derselben Transkription unabhängig zu den Befunden 3.1 und 3.2 (Edge-MI etwa 0,2 Bit, Token-Vorhersagbarkeit unter 1 % der Token-Entropie, Zeilenreset, Space-Vorhersagbarkeit AUC 0,98) und zeigen, dass Chiffren- und Selbstzitat-Generatoren an Edge-Kopplung und Hapax-Reichtum scheitern. Kinnison, "The Voynich Manuscript's positional entropy collapse: comparative evidence from languages and ciphers" (Cryptologia 2026, doi:10.1080/01611194.2026.2697318), zeigt mit strikter Train/Test-Trennung, aber anderer Testmethodik, dass bestimmte Chiffren Voynich-artig niedrige Entropieprofile erzeugen und dass die zusätzliche Information höherer Ordnungen über Manuskriptteile hinweg ungewöhnlich gering ist; Greshko (2025) hat die Naibbe-Chiffre ausdrücklich als Gegenbeispiel konstruiert. Beides ist mit dem hier gemessenen Profil verträglich: Entropie und Token-MI sind durch Chiffren erreichbar, Edge-Kopplung, Hapax-Anteil und Seitenlokalität nach den Tests in Abschnitt 4 nicht gleichzeitig. Neu in diesem Bericht: der Lexikontest (2.4), das Residuum jenseits eines angepassten Automaten als Maß (3.4, 4), die Drift mit dem Folio-Abstand (3.5), die Eliminierung der Substitution mit Chiffrat-Rückkopplung `C_t = T[C_{t-1}, P_t]` (4; das ist kein Alberti-Verfahren, Alberti wechselte das Alphabet nach einigen Wörtern mit Signal im Chiffrat), die Kongruenz- und Richtungstests (3.3), der kontrollierte Hand-gegen-Sektion-Vergleich (3.6; die Koinzidenz selbst ist seit Currier bekannt), der Label-Test (3.7), der Text-gegen-Bild-Test mit Empfindlichkeitskontrolle (3.8), die Robustheitsprüfung (4.1) und vor allem der **positive** Befund, dass ein driftender Automat die vollständige Batterie reproduziert. Ältere Befunde (Currier: Zeile als Einheit; Lindemann & Bowern: ungewöhnlich starke lokale Beschränkung der Glyphen) sind konsistent.

## 7. Grenzen

- Die Mechanismus-Batterie wurde auf der ZL-Transkription gerechnet; die Kernkennzahlen sind auf der Takahashi-Transkription reproduziert (4.1).
- Alle MI-Werte sind Plug-in-Schätzer mit Shuffle-Korrektur; absolute Werte sind stichprobenabhängig, weshalb überall gleich große Stichproben und gleich geschnittene Kontrollen verwendet wurden. Ein früherer Test mit Shuffles, die Randwörter in Mittelpositionen mischten, war deshalb unbrauchbar und wurde ersetzt.
- lzma ist kein optimaler Entropieschätzer; das Residuum ist nur relativ (Text gegen eigenen Zwilling) aussagekräftig.
- Die Rugg- und Timm/Schinner-Generatoren sind eigene Näherungen der publizierten Verfahren; ihre strukturellen Fehlschläge (Edge-Kopplung ≈ 0) folgen aber aus der Konstruktion, nicht aus Parametern.
- Die Folio-Reihenfolge ist nicht sicher die Produktionsreihenfolge.
- Die Bildmerkmale in 3.8 sind grobe Farbstatistiken aus einem 50-dpi-Rendering; sie erfassen Blatt-, Blüten- und Wurzelanteile, nicht Pflanzenidentität. Die Empfindlichkeitsgrenze (etwa 10 bildbestimmte Wörter pro Seite) gilt nur für solche Merkmale. Nur die Folios 1 bis 58 ohne Faltblätter wurden zugeordnet.
- Der Verbose-Chiffre-Generator ist eine mögliche Ausgestaltung, keine erschöpfende; die drei Fehlschläge (Lexikon, Space-Gain, Residuum) sind jedoch Eigenschaften jeder Chiffre, die Klartext-Redundanz erhält.

## 8. Sinnvolle nächste Schritte

- Hypothesen, Kennzahlen und Testset sind eingefroren. Nächster Schritt ist die unabhängige Reproduktion aus diesem Repository, dann Bootstrap-Konfidenzintervalle (Quire-Resampling) und Abbildungen für eine Manuskriptfassung.
- Für 3.8 würden annotierte Bildmerkmale (Pflanzenteile, Blütenform, Anzahl der Pflanzen, Zodiak-Zeichen) die Empfindlichkeit deutlich erhöhen; der Testcode nimmt beliebige Merkmalsvektoren pro Folio.
- Prüfen, ob die Übergangsmatrix des Automaten "entworfen" aussieht (tabellenartige Regelmäßigkeiten, die auf ein konstruiertes System deuten) oder "gewachsen" (glatte Häufigkeitsverteilungen wie bei Gewohnheiten).
- Labels (3.7): prüfen, ob ihre Glyphenstatistik dem Automaten der jeweiligen Hand folgt oder ein eigener Prozess ist; Zirkel- und Radialtexte gesondert.
