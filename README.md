# UK Train Delay Checker

Un projet pour suivre les horaires des trains au Royaume-Uni et détecter les retards.

## 🎯 Fonctionnalités

- ✅ Vérification automatique des retards de train
- ✅ Notifications via GitHub Actions
- ✅ Historique des retards
- ✅ **Utilise TransportAPI (gratuit - 30 requêtes/jour)**

## 🚆 **2 Workflows disponibles**

| Workflow | Trajet | Jour | Heures | Requêtes/jour |
|----------|--------|------|--------|----------------|
| `check-train-delays.yml` | **CRE → EUS** (Aller) | **Jeudi** | 15h00-19h30 | 10 |
| `check-return-train-delays.yml` | **EUS → CRE** (Retour) | **Lundi** | 15h30-18h30 | 7 |

**Total : 17 requêtes/semaine** (plan gratuit compatible ✅)

---

## 🚀 Configuration

### 1️⃣ Obtenir une clé API (GRATUITE)

1. **Va sur [TransportAPI Developer Portal](https://developer.transportapi.com/)**
2. **Insris-toi** avec ton email
3. **Crée une nouvelle application** (Free plan)
4. **Copie tes identifiants** : `app_id` et `app_key`
   - Le plan gratuit donne **30 requêtes par jour** (suffisant pour un usage personnel)
   - Pas de carte bancaire requise

### 2️⃣ Configurer les secrets GitHub

Dans ton repository GitHub (`anoshy9/UK-train`):

1. Va dans **Settings > Secrets > Actions**
2. Ajoute ces **6 secrets** :
   
   **Pour les 2 workflows (Aller + Retour) :**
   - `TRANSPORT_API_ID` : Ton `app_id` de TransportAPI (commun aux 2)
   - `TRANSPORT_API_KEY` : Ton `app_key` de TransportAPI (commun aux 2)
   
   **Pour l'ALLER (CRE → EUS - Jeudi) :**
   - `FROM_STATION` : **`CRE`** (Crewe)
   - `TO_STATION` : **`EUS`** (London Euston)
   
   **Pour le RETOUR (EUS → CRE - Lundi) :**
   - `RETURN_FROM_STATION` : **`EUS`** (London Euston)
   - `RETURN_TO_STATION` : **`CRE`** (Crewe)

> ✅ **Déjà configuré** : Les workflows sont **automatiquement filtrés** pour **London Northwest Railway**.

> ⚠️ **Note** : 
> - Aller (Jeudi) : 10 requêtes/jour
> - Retour (Lundi) : 7 requêtes/jour
> - **Total : 17 requêtes/semaine** (bien en dessous de la limite de 30/jour).

### 3. Codes des gares principales

| Gare | Code |
|------|------|
| London Victoria | VIC |
| London King's Cross | KGX |
| London Euston | EUS |
| London Paddington | PAD |
| London Waterloo | WAT |
| Manchester Piccadilly | MAN |
| Birmingham New Street | BHM |
| Edinburgh Waverley | EDB |
| Glasgow Central | GLC |

## 📁 Structure du projet

```
UK-train/
├── .github/
│   └── workflows/
│       └── check-train-delays.yml  # Workflow GitHub Actions
├── scripts/
│   └── check_train_delays.py       # Script Python principal
├── README.md
└── requirements.txt
```

## 🔧 Installation locale

```bash
# Cloner le repository
git clone https://github.com/anoshy9/UK-train.git
cd UK-train

# Créer un fichier .env
cat > .env << EOF
TRAIN_API_KEY=ta_clé_api_ici
FROM_STATION=VIC
TO_STATION=KGX
DEPARTURE_TIME=08:00
EOF

# Installer les dépendances
pip install -r requirements.txt

# Exécuter le script
python scripts/check_train_delays.py
```

## ⚙️ Personnalisation

### Changer les gares

Modifie les variables d'environnement ou les secrets GitHub:
- `FROM_STATION` : Gare de départ
- `TO_STATION` : Gare d'arrivée

### Changer l'heure

- `DEPARTURE_TIME` : Heure de départ au format HH:MM

### Changer la fréquence

Dans `.github/workflows/check-train-delays.yml`, modifie la ligne `cron`:
```yaml
# Toutes les 15 minutes
- cron: '*/15 * * * *'

# Toutes les heures
- cron: '0 * * * *'

# Tous les jours à 8h
- cron: '0 8 * * *'
```

## 📊 Exemple de sortie

### Train à l'heure
```
✅ TRAIN ON TIME ✅

Train 12345 (Gatwick Express)
Departure: 08:00
Arrival: 08:30
```

### Train en retard
```
⚠️ TRAIN DELAYED ⚠️

Train 67890 (Southern Railway)
From: 08:00 → Expected: 08:15
To: 08:30 → Expected: 08:45
**Delay: 15 minutes**
```

## 🔄 Workflow GitHub Actions

Le workflow s'exécute automatiquement **toutes les 15 minutes** (mais limité à 30 requêtes/jour avec le plan gratuit).

**Fonctionnement :**
1. Vérifie l'état du train via TransportAPI
2. Génère un rapport dans `train_status.txt`
3. Peut être déclenché manuellement depuis GitHub

> ⚠️ **Avec le plan gratuit (30 requêtes/jour)** :
> - Le workflow s'exécutera **2 fois par jour** (toutes les 12h)
> - Pour plus de fréquence, réduis la fréquence dans `.github/workflows/check-train-delays.yml`
> - Ou passe à un plan payant sur TransportAPI

## 📝 Historique

Pour garder un historique des retards:

1. Crée un fichier `delay_history.md`
2. Ajoute ce script à la fin de ton workflow:

```yaml
- name: Update history
  run: |
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $(cat train_status.txt)" >> delay_history.md
    git config --global user.name "GitHub Actions"
    git config --global user.email "actions@github.com"
    git add delay_history.md
    git commit -m "Update delay history"
    git push
```

## 🚨 Notifications

Pour recevoir des notifications:

### Option 1: Email via GitHub
1. Active les notifications dans ton compte GitHub
2. Le workflow enverra un email si le train est en retard

### Option 2: Discord/Slack
Ajoute une étape de notification dans le workflow:

```yaml
- name: Send Discord notification
  if: steps.check.outputs.is_delayed == 'true'
  uses: Ilshidur/action-discord@0.6.4
  with:
    args: "Train en retard ! {{ steps.check.outputs.message }}"
  env:
    DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
```

## 🔍 Trouver les codes des gares

### Méthode 1 : Recherche directe via TransportAPI
Le script peut **trouver automatiquement le code** si tu donnes le nom de la gare.

### Méthode 2 : Liste des gares principales

| Ville | Gare | Code (CRS) |
|-------|------|------------|
| Londres | Victoria | `VIC` |
| Londres | King's Cross | `KGX` |
| Londres | Euston | `EUS` |
| Londres | Paddington | `PAD` |
| Londres | Waterloo | `WAT` |
| Londres | Liverpool Street | `LST` |
| Londres | Bridge | `LBG` |
| Manchester | Piccadilly | `MAN` |
| Birmingham | New Street | `BHM` |
| Edinburgh | Waverley | `EDB` |
| Glasgow | Central | `GLC` |
| Bristol | Temple Meads | `BRM` |
| Leeds | Station | `LDS` |
| Brighton | Station | `BTN` |

### Méthode 3 : Recherche complète
Utilise ce script pour trouver le code de n'importe quelle gare :

```python
import requests

def find_station(name):
    url = "https://transportapi.com/v3/uk/places.json"
    params = {
        'query': name,
        'type': 'train_station',
        'app_id': 'TON_APP_ID',
        'app_key': 'TON_APP_KEY'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'member' in data:
        for station in data['member']:
            print(f"{station['name']}: {station['station_code']}")
    
find_station("Victoria")  # Exemple
```

### Méthode 4 : Site officiel
- [National Rail Station Finder](https://www.nationalrail.co.uk/stations)

## 🔄 Alternatives (si 30 requêtes/jour ne suffisent pas)

### 1. Realtime Trains Scraper (Illimité & Gratuit)
**🔗 [GitHub - Realtime-Trains-Scraper](https://github.com/diamonddigitaldev/Realtime-Trains-Scraper)**

- **100% gratuit et illimité** (pas de clé API)
- Basé sur Node.js
- Données en temps réel

### 2. Trackside (Auto-hébergé)
**🔗 [GitHub - Trackside](https://github.com/carbonarok/trackside)**

- **Open-source et auto-hébergeable**
- Pas de limites (tu contrôles ton serveur)
- Nécessite un Raspberry Pi ou un VPS

### 3. TransportAPI Plan Payant
**🔗 [TransportAPI Pricing](https://developer.transportapi.com/)**

- **500 requêtes/jour** : ~£5/mois
- **5000 requêtes/jour** : ~£25/mois
- Idéal pour un usage intensif

---

## 📄 Licence

MIT

---

Créé avec ❤️ pour les voyageurs du Royaume-Uni

> ⚠️ **Note importante** : TransportAPI limite le plan gratuit à **30 requêtes par jour**. 
> Avec le workflow actuel (toutes les 15 min), tu atteindras cette limite en **7-8 heures**. 
> **Solution** : Modifie la fréquence dans `.github/workflows/check-train-delays.yml` (ex: `0 */12 * * *` pour 2 fois par jour)
