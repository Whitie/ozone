.. index:: Bestellsystem, Bestellen, Allgemeines

.. include:: /includes.txt

Allgemeines
===========

.. sectionauthor:: |wet|

Auf dieser Seite befindet sich eine kurze Zusammenfassung der Funktionen des neuen
Bestellsystems. Das System ermöglicht es, Bestellungen online zu machen und den
Weg der Bestellung zu verfolgen. Für Benutzer mit besonderen Funktionen
(Besteller: |paa|, |hoed|, |otb|) und Fachbereichsleiter: |wib|, |brc|) stehen
erweiterte Funktionen zur Verfügung (:doc:`verwalten`).

Zugang und Anmeldung
--------------------

Das Bestellsystem ist in die neue :doc:`Datenbank </bbz_datenbank/index>`
integriert, Zugangsmöglichkeiten können hier: :ref:`db-zugang` nachgelesen werden.

Rechtesystem
------------

Siehe: :ref:`db-rechte`

Bestellen
---------

Um Artikel bestellen zu können, wird nachfolgend der Bestellvorgang Schritt für
Schritt erläutert. Grundsätzlich gibt es **drei** Möglichkeiten etwas zu bestellen:

1. `Vormals bestellten Artikel wieder bestellen`_
2. `Bei bereits bestelltem Artikel die Anzahl erhöhen`_
3. `Neuen Artikel bestellen`_

.. important:: Es können nur Artikel bestellt werden, für die ein Lieferant
   in der Datenbank vorhanden ist. Siehe `Lieferant anlegen`_.

Auf der Startseite des Bestellsystems (Klick links oben auf Bestellsystem) finden Sie
eine Übersicht der kommenden Bestelltage (der grüne Button auf dem Bild unten ist
nicht für jeden Benutzer sichtbar). Sie können durch einen Klick auf einen
Bestelltag alle vorhandenen Bestellungen für diesen Termin einsehen. Unten auf der
Seite werden die letzten Lieferungen für den derzeit angemedelten Benutzer angezeigt.

.. _bestell-startseite:

.. figure:: /images/bestellsystem/startseite.*
   :scale: 50 %

   Bestellungen - Startseite

Vormals bestellten Artikel wieder bestellen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Links im Menü befindet sich der Punkt
:menuselection:`Bestellungen --> Meine Bestellungen`. Dort finden Sie **alle**
Bestellungen, die Sie jemals gemacht haben. Für jeden Status gibt es eine Tabelle,
die über die Buttons oben auf der Seite angesprungen werden können.
Über das kleine Suchfeld rechts oben in jeder Tabelle lassen sich die Datensätze
nach Artikel oder Lieferant filtern.

.. image:: /images/bestellsystem/meine_bestellungen.*
   :scale: 50 %

In der ganz rechten Spalte dieser Tabelle befindet sich ein Link 'Neu bestellen'. Durch
Anklicken dieses Links kommt man in das *große* `Bestellformular`_, wobei fast alle
Daten des Artikels schon übernommen werden (Anzahl muss neu eingegeben werden).

.. image:: /images/bestellsystem/bestellen_alt.*

Jetzt **müssen** noch die Kostenstellen eingegeben werden.Nach einem Klick auf
'Jetzt bestellen' wird die Bestellung in der Datenbank abgelegt und ist über den
Bestelltag (siehe Bild :ref:`bestell-startseite`) jederzeit einsehbar (Anzahl auch
änderbar, siehe nächster Abschnitt).

Bei bereits bestelltem Artikel die Anzahl erhöhen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Über die :ref:`bestell-startseite` gelangt man durch den Klick auf einen Bestelltag
in die Übersicht aller Bestellungen. Hier kann man sehen, wer was bestellt hat.
Eigene Bestellungen können hier auch gelöscht werden.  Über das kleine Suchfeld rechts
oben in der Tabelle lassen sich die Datensätze nach Artikel oder Lieferant filtern.

.. note:: Eigene Bestellungen können nur gelöscht werden, wenn sich noch kein
   anderer Benutzer mit eingetragen hat und die Bestellung noch nicht ausgelöst wurde.

.. _offene-bestellungen:

.. figure:: /images/bestellsystem/bestelltag.*
   :scale: 70 %

   Offene Bestellungen

Wenn der gewünschte Artikel gefunden wurde **und** sich noch im `Status`_
*neu* befindet, kann die Anzahl nach Wunsch geändert werden. Dabei wird automatisch
der eigene Name mit in die Liste der Besteller eingetragen. Die Änderung erfolgt
durch anpassen der Anzahl und verlassen des Eingabefeldes mit dem Cursor.

Status
''''''

Die Spalte Status kann folgende Zustände haben:

.. |accepted| image:: /images/bestellsystem/accepted.*

.. |rejected| image:: /images/bestellsystem/rejected.*

.. |ordered| image:: /images/bestellsystem/ordered.*

.. |delivered| image:: /images/bestellsystem/delivered.*

.. |new| image:: /images/bestellsystem/new.*

.. csv-table:: Status
   :header: "Name", "Symbol", "Bedeutung"
   :widths: 20, 30, 70

   "Neu", |new|, "Bestellung wurde neu eingegeben, Änderung der Anzahl möglich"
   "Akzeptiert", |accepted|, "Bestellung wurde durch Fachbereichsleiter geprüft und genehmigt, keine Änderung der Anzahl mehr möglich"
   "Zurückgewiesen", |rejected|, "Bestellung wurde durch Fachbereichsleiter abgelehnt"
   "Bestellt", |ordered|, "Bestellung wurde ausgelöst"
   "Geliefert", |delivered|, "Bestellung ist ganz oder teilweise eingetroffen, dieser Status wird z. Z. noch nicht benutzt"

Die Symbole treten auch ohne Beschriftung auf. Sie haben aber immer die gleiche farbliche
Umrandung. Sie Spalte Status in :ref:`offene-bestellungen`.

Neuen Artikel bestellen
~~~~~~~~~~~~~~~~~~~~~~~

Über das Menü :menuselection:`Bestellungen --> Jetzt bestellen` gelangt man zu einer
Seite, die zwei Möglichkeiten der Bestellung bietet. Bestellen eines Artikels aus der
Datenbank oder bestellen eines neuen Artikels.

.. figure:: /images/bestellsystem/bestellen_auswahl.*

   Bestellauswahl

Das Eingabefeld für bereits vorhandene Artikel bietet Auto-Vervollständigung und
aktualisiert sich bei jedem eingegebenen Buchstaben. Hier können Artikelnamen,
Artikelnummern und Strichcodes eingegeben werden.

.. image:: /images/bestellsystem/bestellen_vorhanden.*

Ist der gewünschte Artikel bereits in der Datenbank vorhanden, kann er nun
ausgewählt werden und nach einem Klick auf 'weiter' gelangt man zum *großen*
`Bestellformular`_. Jetzt geht es weiter wie unter
`Vormals bestellten Artikel wieder bestellen`_ im letzten Absatz beschrieben.

Klickt man unter 'Neuen Artikel bestellen' auf 'weiter', gelangt man in das *große*
`Bestellformular`_, welches in diesem Fall leer ist.

Hier kann man nun alle Angaben zum Artikel machen. Der Artikel wird automatisch in die
Datenbank übernommen und steht dann für weitere Bestellungen allen zur Verfügung.
Über 'Jetzt bestellen' wird die Bestellung dann abgeschickt. Sollte ein Pflichtfeld
nicht ausgefüllt sein oder die Kostenstellen nicht 100 in Summe ergeben, erhalten Sie
eine entsprechende Meldung und können dieses korrigieren. Nach der Korrektur muss
erneut auf 'Jetzt bestellen' geklickt werden.

.. important:: Der Lieferant muss schon vorhanden sein!

Bestellformular
---------------

Im *großen* Bestellformular gibt es zusätzlich zu den normalen Angaben (Artikelname,
Artikelnummer, Lieferant, usw. ) einige neue Felder:

#. **Bestelltag**

   Hier kann der Bestelltag für die Bestellung ausgewählt werden. Voreinstellung ist
   immer der nächstmögliche Bestelltag. Es kann aber auch ein späterer Bestelltag
   gewählt werden.

#. **Memo**

   Wenn man das Wort Memo anklickt, öffnet sich ein Feld zur Texteingabe. Hier kann
   man dem ausführenden Besteller eine Nachricht zukommen lassen.

#. **Prüfung**

   Hier kann ein Häckchen gesetzt werden, wenn die Bestellung für eine Prüfung ist.

#. **Reparatur**

   Hier kann das Häckchen gesetzt werden, wenn Ersatzteile für eine Reparatur
   bestellt werden.

.. note:: Die Informationen 'Prüfung' und 'Reparatur' werden den Bestellern und den
   Fachbereichsleitern unter dem Punkt
   :menuselection:`Bestellungen --> Bestellungen verwalten` angezeigt.

.. image:: /images/bestellsystem/bestellen_neu.*
   :scale: 60 %

Lieferant anlegen
-----------------

Um Bestellungen bei neuen Lieferanten aufzugeben, muss dieser erstmal in der
Datenbank angelegt werden. Hierzu gibt es im Menu unter
:menuselection:`Bestellungen --> Neuer Lieferant` ein verkürztes Formular, mit dem
jeder angemeldete Benutzer Lieferanten anlegen kann.

.. image:: /images/bestellsystem/lieferant_neu.*
   :scale: 75 %

In dieses Formular **muss** der Name **und** mindestens eine Kontaktmöglichkeit
(Festnetz, Fax, Email) eingegeben werden. Die restlichen Angaben sind optional.
Nach absenden des Formulars über den Button 'Sichern', steht der Lieferant im
Bestellformular zur Auswahl zur Verfügung.

Nach der ersten Bestellung bei einem neuen Lieferanten müssen die Kontaktdaten
(Kundennummer, Adresse, Ansprechpartner, usw.) über die Verwaltung vervollständigt
werden. Das ausführliche Formular ist nur für Mitarbeiter der Verwaltung zugänglich.

Feeds
-----

.. versionadded:: 2.99.1

Die letzten Bestellungen und die letzten Lieferungen (pro Benutzer und insgesamt)
stehen als sogenannte `RSS`_-Feeds zur Verfügung. Sie lassen sich über einen
Feed-Reader (z. B. `Outlook`_) bzw. Browser (Firefox: `dynamische Lesezeichen`_)
anzeigen/abonnieren. Die Links zu den Feeds befinden sich auf der
:ref:`bestell-startseite` am rechten Rand.

.. figure:: /images/bestellsystem/rss.*

   RSS-Feeds für das Bestellsystem

.. _RSS: https://de.wikipedia.org/wiki/RSS

.. _Outlook: http://office.microsoft.com/de-de/outlook-help/abonnieren-eines-rss-feeds-HA010355679.aspx#_Toc288635727

.. _dynamische Lesezeichen: http://xml-rss.de/rss-feed-leicht-und-verstaendlich-erklaert/rss-feed-mit-dem-firefox-browser.htm
