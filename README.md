# oorep_importer

## Description

A few Python3 scripts in order to convert and then import repertory data to OOREP (https://www.oorep.com/).

## Prerequisites

A prerequisite of this code is the Python parsita module (https://github.com/drhagen/parsita).

Another prerequisite is that the repertory has been "pre-converted" from the raw sources into the following
human-readable, pretty much self-explanatory plain-text format:

```
= Schweiss
== Allgemein, Neigung zu Schweiß, usw.: Agar. (2) Ant-t. Calc. (2) Chin. (2) Ferr. (2) Graph. (2) Hep. Kali-c. Lach. Lyc. (2) Merc. Nat-c. (2) Nat-m. Nux-v. (2) Op. Ph-ac. (2) Phos. (2) Samb. Sep. (2) Stann. Staph. Sulph. (2) Verat. (2)
=== einseitig: Bar-c. (2) Chin. Nux-v. (2) Phos. Puls. Sulph.
==== rechts: Phos. PULS.
==== links: Bar-c. Chin.
=== einzelne Teile: Apis, Bar-c. Calc. (3) Carb-v. Nux-v. Phos. Puls. (2) Sel. Sep. (3) Sil. (2) Sulph. (2) Thuj. (2) Verat.
=== Erwachen, beim: Dros. Par. Samb. (2) Sep. Sulph.
=== gebadet in Schweiß: Apis, Bell. (2) Colch. (2) Ip. Lach. Phos. Samb. Valer. (2)
=== gelb färbend, die Wäsche: Bell. Carb-an. Graph. Lach. (2) Merc. (2) Sel.
=== heiß: Bell. (2) Cham. (2) Ign. Ip. Op. (2) Sabad. Sep. Stann. Stram. Viol-t.
=== Juckreiz, verursacht: CHAM. Op. Rhus-t.
=== kalt: Ant-t. Ars. Camph. Carb-v. (2) Chin. Merc. Sec. Verat. (2)
==== Stirn, an der: Ant-t. Carb-v. Cina Merc-c. Op. Verat. (3)
=== scharf: Fl-ac.
=== unterdrückt: Acon. Bell. Bry. Cham. (2) Chin. (2) Coloc. Dulc. Lach. (2) Rhus-t. (2) Sil. Sulph. (2)
== Entblößen, Abneigung gegen: Clem. Graph. Hep. Nat-c. Nux-v. Rhus-t. Samb. (2) Stront-c.
== erleichtert nicht: Bell. (2) Dig. Form. Merc. (3) Op.
== Zudecken, Hitze, usw. amel.: Clem. (2) Hep. Nux-v. (3) Rhus-t. Stront-c. (2)
```

where the number of trailing `=`-characters shows the depth of a (sub-) rubric with respect to its parent rubric.
Chapters (i.e., root rubrics) have therefore only a single trailing `=`-character. Every rubric occupies exactly a
single line in the input file.

## Usage

The workflow of conversion is outlined in `__main__.py` and some further examples given in the accompanying unit
tests.

## Caveat

There is virtually no error handling in the Python code. That's ok. You're meant to know what you're doing.

---

## What next?

Usually, you want to apply those additions to your local dev-db first, and then transfer those changed tables to the
production-db. For sake of completeness, those PostgreSQL-commands are summarised in the following:
- Create local dump: `PGPASSWORD="..." pg_dump -h localhost -U oorep_user oorep -Fc -p 5432 > ~/dump.pg`
- Upload `dump.pg` to server
- On production server, drop table `remedy`, for example
- On production server, then restore table `remedy`: `PGPASSWORD="..." pg_restore -h localhost -U oorep_user -d oorep -t remedy dump.pg`
- Proceed equally with all other modified tables
