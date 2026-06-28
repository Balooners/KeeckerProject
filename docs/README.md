# Documentation Reverse Engineering

Ce dossier est le point d'entree de la documentation technique KeeckerOS.

La structure proposee separe les preuves brutes, les acquisitions, les analyses, les syntheses d'architecture et les conclusions. Les contenus existants ne sont pas deplaces: ils restent accessibles depuis les index et pourront etre classes progressivement.

## Structure cible

```text
docs/
  00-Governance/       Methodologie, conventions, perimetre, securite.
  01-Architecture/     Syntheses systeme et vues multi-couches.
  02-Acquisition/      Methodes de collecte et chaine de conservation.
  03-Evidence/         Inventaires de preuves et references d'artefacts.
  04-Analysis/         Analyses techniques reproductibles.
  05-Interfaces/       Binder, JNI, HTTP, ADB, protocoles et API.
  06-Firmware/         APK, ODEX, OAT, images systeme et runtime Android.
  07-Hardware/         Plateforme physique, bus, capteurs, actionneurs.
  08-Network/          Cartographie reseau, services et captures.
  09-Findings/         Decouvertes validees, hypotheses et questions.
  10-Operations/       Procedures, commandes et runbooks.
  90-Archive/          Anciennes notes conservees pour tracabilite.
  _templates/          Modeles de fiches et d'index.
```

## Regles de classement

- Une affirmation technique doit pointer vers une preuve, une commande, un hash, un log ou un artefact.
- Les fichiers binaires et exports bruts restent hors des syntheses, dans les dossiers d'artefacts dedies.
- Les journaux chronologiques restent des journaux; les conclusions stabilisees vont dans `09-Findings/`.
- Les dossiers historiques non numerotes dupliques sont archives sous `90-Archive/legacy-docs/`.

Voir [INDEX.md](INDEX.md) pour la navigation complete.
