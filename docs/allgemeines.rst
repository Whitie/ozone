.. index:: DB, Zugang

.. include:: /includes.txt

Allgemeines
===========

.. sectionauthor:: |wet|

Auf dieser Seite befindet sich eine kurze Zusammenfassung der Funktionen der neuen
Datenbank (Ozone Software). Mit der Software werden Azubis (mit Anwesenheiten),
Firmen (Kooperationspartner und Lieferanten), Bestellungen (mit Wareneingang),
Mitarbeiter (auch externe Dozenten), pädagogische Tagebücher und Arbeitsunfälle
im bbz Chemie verwaltet.

.. _db-zugang:

Zugang und Anmeldung
--------------------

Durch Aufruf der Adresse |db_url| im Browser (bitte nicht mit dem Internet Explorer)
gelangt man auf die Startseite der Datenbank. Dort kann man sich mit seinen normalen
Windows Anmeldedaten einloggen.

.. image:: /images/db/startseite.*
   :scale: 75 %

.. _db-rechte:

Rechtesystem
------------

Das System arbeitet ähnlich wie Windows mit Gruppen. Je nach Zugehörigkeit stehen
die im Weiteren beschriebenen Funktion ganz, teilweise oder nicht zur Verfügung
(z. B. dürfen Firmen nur von der Gruppe Verwaltung angelegt und geändert werden,
Gesprächsnotizen darf aber jeder hinzufügen). Bestellen kann jeder, Bestellungen
genehmigen oder auslösen nur bestimmte Gruppen.

Dateneingabe
------------

Damit die Datenbank alle Verknüpfungen richtig erstellen kann, ist bei der
Dateneingabe eine gewisse Reihenfolge einzuhalten. Die Eingabe der meisten Daten
erfolgt über die Administration (nur Verwaltung, oben im Menü). Einige Formulare
(neuer Azubi, neuer Dozent) sind über die normale Oberfläche erreichbar.

.. image:: /images/db/azubi_neu.*
   :scale: 50 %

.. image:: /images/db/dozent_neu.*
   :scale: 40 %

Hierzu einige Beispiele:

Azubis
~~~~~~

Azubis können erst (sinnvoll) angelegt werden, wenn die entsprechende Gruppe
(z. B. CL 2012) existiert **und** die jeweilige Firma. Um trotzdem Testteilnehmer
zu erfassen, ist es aber möglich, Azubis ohne Gruppe und Firma anzulegen.

Kooperationsverträge
~~~~~~~~~~~~~~~~~~~~

Kooperationsverträge können erst angelegt werden, wenn die Firma existiert.

Lieferantenbewertungen
~~~~~~~~~~~~~~~~~~~~~~

Bewertungen können auch erst gemacht werden, wenn die Firma existiert.

Anwesenheiten
~~~~~~~~~~~~~

Anwesenheiten können erst erfasst werden, wenn der Azubi inkl. Gruppe und Firma
angelegt ist.

.. note::

   Wenn eine Gruppe Azubis enthält, die keiner Firma zugeordnet sind, ist die
   Anwesenheitsliste nicht aufrufbar. Es gibt eine Fehlermeldung.

Kontakte
~~~~~~~~

Kontakte können nur zu einer bereits angelegten Firma gespeichert werden. Wenn
Kontakte zu einer Firma angelegt sind, können bei Telefonaten Gesprächsnotizen
angelegt werden. Diese sind von **jedem** angemeldeten Benutzer einsehbar.

Datenabfrage
------------

Zur Abfrage von Firmen- und Azubidaten ist generell jeder angemeldete Benutzer
berechtigt. Die Abfrage ist alphabetisch oder über eine Suche möglich (Azubis
und Firmen). Zum Teil werden Informationen oder Buttons für bestimmte Gruppen
ausgeblendet (z. B. der "Firma hinzufügen" Button auf dem Bild unten).

.. image:: /images/db/abfrage.*
   :scale: 75 %

