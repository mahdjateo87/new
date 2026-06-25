# Guide d'installation — Gestion des Gardes Clinique ALOUIA

**Pour :** Mahdjate Oussama — Chef de bloc  
**Clinique :** ALOUIA, Birtouta

---

## Ce dont vous avez besoin


| Élément             | Détail                                                  |
| ------------------- | ------------------------------------------------------- |
| Ordinateur          | Windows 10 ou Windows 11                                |
| Connexion           | Internet (uniquement pour la première installation)     |
| Espace disque       | Environ 100 Mo                                          |
| Clé USB (optionnel) | Pour copier l'application et l'utiliser sur un autre PC |


---

## MÉTHODE 1 — La plus simple (recommandée)

### Étape 1 : Télécharger le projet

1. Allez sur GitHub : [https://github.com/mahdjateo87/new](https://github.com/mahdjateo87/new)
2. Cliquez sur le bouton vert **Code**
3. Choisissez **Download ZIP**
4. Extrayez le fichier ZIP sur votre Bureau (clic droit → Extraire tout)

Vous obtenez un dossier nommé `new` ou `new-main`.

---

### Étape 2 : Installer Python (si pas déjà installé)

1. Allez sur [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Téléchargez **Python 3.12** (ou plus récent)
3. **IMPORTANT** : cochez la case ✅ **"Add Python to PATH"** en bas de la fenêtre
4. Cliquez **Install Now**
5. Attendez la fin, puis fermez

Pour vérifier : ouvrez l'invite de commandes (touche Windows + R → tapez `cmd` → Entrée) et tapez :

```
python --version
```

Vous devez voir : `Python 3.12.x`

---

### Étape 3 : Installer l'application

1. Ouvrez le dossier extrait
2. Dans la barre d'adresse en haut, tapez `cmd` et appuyez sur **Entrée**
  → Une fenêtre noire s'ouvre directement dans le bon dossier
3. Tapez ces commandes **une par une** (appuyez sur Entrée après chaque ligne) :

```
pip install -r requirements.txt
```

```
python app\main.py
```

4. L'application s'ouvre !

---

### Étape 4 : Premier lancement (configuration)

Une fenêtre s'affiche. Remplissez :


| Champ              | Exemple               |
| ------------------ | --------------------- |
| Nom de la clinique | Clinique ALOUIA       |
| Lieu               | Birtouta              |
| Chef de service    | Mahdjate Oussama      |
| Seuil surcharge    | 176 (heures par mois) |


Cliquez **Enregistrer et démarrer**.

---

### Étape 5 : Créer le raccourci sur le bureau

1. Ouvrez le dossier `installer` dans le projet
2. **Clic droit** sur `install_windows.bat`
3. Choisissez **Exécuter en tant qu'administrateur**
4. Suivez les instructions à l'écran
5. Un raccourci **Gardes Clinique ALOUIA** apparaît sur votre Bureau

---

## MÉTHODE 2 — Exécutable portable (clé USB)

Idéal si vous voulez utiliser l'application sur plusieurs PC sans réinstaller.

### Étape 1 : Créer l'exécutable (une seule fois)

Sur un PC avec Python installé :

1. Ouvrez `cmd` dans le dossier du projet
2. Tapez :

```
installer\build_windows.bat
```

1. Attendez 2 à 5 minutes
2. Le fichier est créé dans : `installer\dist\CliniqueAlouiaGardes.exe`

### Étape 2 : Copier sur clé USB

1. Branchez votre clé USB
2. Copiez `CliniqueAlouiaGardes.exe` sur la clé
3. Sur n'importe quel PC Windows : double-cliquez sur le fichier

> Aucune installation nécessaire — l'application fonctionne directement depuis la clé USB.

---

## MÉTHODE 3 — Tester sans interface graphique (démonstration)

Pour vérifier que tout fonctionne (import Excel, comptage, export) :

```
python demo.py
```

Cette commande affiche dans la console :

- L'import de votre fichier Excel exemple
- Le comptage des heures par personne
- Les fichiers Excel et PDF générés

---

## Utilisation quotidienne

```
┌─────────────────────────────────────────────────────────┐
│  1. Ouvrir l'application (raccourci Bureau)             │
│  2. Onglet PERSONNEL → ajouter l'équipe                  │
│  3. Onglet LISTE DE GARDE → cliquer sur une case       │
│     pour assigner une personne ou signaler :              │
│       [A] = Absence    [R] = Retard    [C] = Congé      │
│  4. Onglet COMPTAGE → voir les heures du mois           │
│     (lignes rouges = surcharge)                         │
│  5. Bouton EXPORTER EXCEL → imprimer ou envoyer par mail│
└─────────────────────────────────────────────────────────┘
```

### Importer votre ancien fichier Excel

1. Onglet **Liste de garde**
2. Cliquez **Importer Excel**
3. Sélectionnez votre fichier `.xlsx` (ex: `liste_de_garde_instrumentiste.xlsx`)
4. Cliquez **Enregistrer**

### Colonnes par service (comme votre Excel)

**Instrumentiste :**

```
Journalier 08H-16H          │  Nuit 16H-08H
mat      │ chir │ chir │ chir │  mat     │ chir
salle 4  │ s.1  │ s.2  │ s.3  │  salle 4 │ 
```

**Femme d'hygiène :**

```
Journalier 08H-16H    │  Nuit 16H-08H
mat  │ chir           │  mat  │ chir
```

**Stérilisation :**

```
08H-16H  │  Nuit 16H-08H  │  24H  │  2 sur 2
```

> Pour modifier les colonnes : onglet **Paramètres** → **Modifier service sélectionné**

---

## Où sont stockées vos données ?

Toutes vos données restent sur votre PC (pas sur internet) :

```
C:\Users\VOTRE_NOM\AppData\Roaming\CliniqueAlouiaGardes\
```

Pour sauvegarder : copiez ce dossier sur une clé USB.

---

## Problèmes fréquents


| Problème                     | Solution                                              |
| ---------------------------- | ----------------------------------------------------- |
| `python` n'est pas reconnu   | Réinstallez Python en cochant **Add to PATH**         |
| L'application ne s'ouvre pas | Essayez `pythonw app/main.py`                         |
| Erreur à l'import Excel      | Vérifiez que le fichier est bien `.xlsx` (pas `.xls`) |
| Email ne part pas            | Renseignez le serveur SMTP dans **Paramètres**        |
| Pas de raccourci bureau      | Relancez `install_windows.bat` en administrateur      |


---

## Aide rapide

- **Démonstration console :** `python demo.py`
- **Lancer l'application :** `python app/main.py`
- **Fichier exemple :** `examples/exemple_liste_garde_instrumentiste.xlsx`

---

*Mahdjate Oussama — Clinique ALOUIA, Birtouta*