# Gestion des Gardes — Clinique ALOUIA (Birtouta)

Application de gestion des listes de garde pour le bloc opératoire de la **Clinique ALOUIA**, développée pour **Mahdjate Oussama**, chef de bloc.

## Fonctionnalités

- **3 services** : Instrumentiste, Femme d'hygiène, Stérilisation
- **Types de vacation personnalisables** par service :
  - `08H16H`, `16H08H`, `24H`, `16H22H`, `2SUR2`, `2JOUROFF`, `2JOURON`
- **Liste de garde** modifiable (remplacement d'urgence, absence, retard, congé)
- **Comptage mensuel** des vacations et heures par personne
- **Détection de surcharge** (seuil d'heures configurable)
- **Export / import Excel** (format compatible avec vos fichiers existants)
- **Formulaires imprimables** : demande de congé, planning des congés (PDF)
- **Impression et envoi par email** des listes de garde et comptages
- **Configuration initiale** : nom de la clinique et chef de service modifiables

## Installation sur Windows

📖 **Guide détaillé pas à pas : voir [GUIDE_INSTALLATION.md](GUIDE_INSTALLATION.md)**

### Démonstration rapide (sans interface graphique)

```bash
pip install -r requirements.txt
python demo.py
```

### Lancer l'application complète

```bash
pip install -r requirements.txt
python app/main.py
```

### Option 1 — Installateur (recommandé)

1. Copiez le dossier `installer` sur votre PC (ou clé USB)
2. Exécutez `install_windows.bat` en tant qu'administrateur
3. Un raccourci **Gardes Clinique ALOUIA** sera créé sur le bureau

### Option 2 — Exécutable portable (clé USB)

1. Sur un PC avec Python, lancez `installer/build_windows.bat`
2. Copiez `installer/dist/CliniqueAlouiaGardes.exe` sur votre clé USB
3. Double-cliquez pour lancer depuis n'importe quel PC Windows

### Option 3 — Lancement avec Python

```bash
pip install -r requirements.txt
python app/main.py
```

## Utilisation

1. **Premier lancement** : renseignez le nom de la clinique, le lieu et le chef de service
2. **Personnel** : ajoutez votre équipe (instrumentistes, hygiène, stérilisation)
3. **Paramètres** : personnalisez les vacations et colonnes par service
4. **Liste de garde** : cliquez sur une cellule pour assigner une personne ou signaler absence/retard/congé
5. **Comptage** : consultez les heures mensuelles et les surcharges
6. **Congés** : créez des demandes et imprimez les formulaires PDF

## Données

Les données sont stockées localement dans :
- Windows : `%APPDATA%\CliniqueAlouiaGardes\`
- Linux : `~/.local/share/CliniqueAlouiaGardes/`

## Import de vos fichiers Excel existants

Utilisez **Importer Excel** dans l'onglet Liste de garde pour charger vos anciens fichiers `.xlsx`.

## Auteur

Mahdjate Oussama — Chef de bloc, Clinique ALOUIA, Birtouta
