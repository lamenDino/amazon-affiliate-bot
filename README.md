# 🔗 Amazon Affiliate Link Bot - Telegram (Render Edition)

Bot Telegram che converte link Amazon in link di affiliazione accorciati usando **YOURLS** su Render.

## ✨ Funzionalità

- ✅ Estrae link Amazon dal messaggio Telegram
- ✅ Aggiunge il tuo tag di affiliazione (es: `ruciferia-21`)
- ✅ Accorcia il link usando **YOURLS** (self-hosted)
- ✅ Supporta **tutti gli store Amazon mondiali** (.it, .com, .es, .fr, .de, .co.uk, ecc.)
- ✅ Risposta formattata in Markdown
- ✅ Deploy su Render in 5 minuti

## 🚀 Deploy Rapido su Render

### 1. **Fork o Clona il Repository**

```bash
git clone https://github.com/lamendino/amazon-affiliate-bot.git
cd amazon-affiliate-bot
```

### 2. **Crea Due Servizi su Render**

#### Servizio 1: YOURLS (Database + App)

1. Vai su https://render.com → **New +** → **PostgreSQL**
2. Configura:
   - **Name**: `yourls-db`
   - **Database**: `yourls`
   - Salva le credenziali

3. Crea nuovo servizio → **Web Service** → Deploy da GitHub
4. Configura:
   - **Name**: `amazon-affiliate-yourls`
   - **Environment**: Docker
   - **Build Command**: (lascia vuoto)
   - **Start Command**: (lascia vuoto - Render lo rileva)

5. Aggiungi variabili d'ambiente:
   ```
   YOURLS_DB_HOST=yourls-db.c6ab.render.com
   YOURLS_DB_USER=yourls_user
   YOURLS_DB_PASS=tua_password_forte
   YOURLS_DB_NAME=yourls
   YOURLS_SITE=https://amazon-affiliate-yourls.onrender.com
   YOURLS_USER=admin
   YOURLS_PASS=tua_password_admin_forte
   ```

6. Deploy

#### Servizio 2: Bot Telegram

1. Crea nuovo servizio → **Web Service** → Deploy da GitHub
2. Configura:
   - **Name**: `amazon-affiliate-bot`
   - **Environment**: Docker
   - **Root Directory**: `.` (radice del progetto)

3. Aggiungi variabili d'ambiente:
   ```
   TELEGRAM_TOKEN=8192598584:AAHuV4Gv1X9KY0V5RHOYKyxykw4TJuko1Wo
   YOURLS_URL=https://amazon-affiliate-yourls.onrender.com
   YOURLS_SIGNATURE=your_signature_here
   AFFILIATE_TAG=ruciferia-21
   ```

4. Deploy

### 3. **Ottieni YOURLS Signature**

1. Apri `https://amazon-affiliate-yourls.onrender.com/admin`
2. Accedi con:
   - Username: `admin`
   - Password: (la password che hai impostato)

3. Vai a **Tools** → **API**
4. Copia la **Signature**
5. Torna su Render → Bot Service → **Environment** → Modifica `YOURLS_SIGNATURE`
6. Salva e il bot si riavvierà automaticamente

---

## 📝 Variabili d'Ambiente

### Bot Service

```env
TELEGRAM_TOKEN=tuo_token_telegram
YOURLS_URL=https://amazon-affiliate-yourls.onrender.com
YOURLS_SIGNATURE=tua_signature_yourls
AFFILIATE_TAG=ruciferia-21
```

### YOURLS Service

```env
YOURLS_DB_HOST=tuo_host_database
YOURLS_DB_USER=yourls_user
YOURLS_DB_PASS=password_forte
YOURLS_DB_NAME=yourls
YOURLS_SITE=https://amazon-affiliate-yourls.onrender.com
YOURLS_USER=admin
YOURLS_PASS=password_admin
```

---

## 📱 Utilizzo

Invia un link Amazon al bot:

```
https://www.amazon.it/Smartphone-MediaTek-Dimensity-processore-Caricabatterie/dp/B0FHBS428L/
```

Riceverai:

```
✅ Link di affiliazione creato:

[https://amazon-affiliate-yourls.onrender.com/abc123](https://amazon-affiliate-yourls.onrender.com/abc123)
```

---

## 🔧 Troubleshooting su Render

### Bot non risponde

1. Vai su Render Dashboard → Bot Service → **Logs**
2. Verifica i log per errori
3. Controlla che `TELEGRAM_TOKEN` sia corretto

### Errore "Connection refused" per YOURLS

1. Verifica che il servizio YOURLS sia "Live"
2. Attendi 5 minuti dopo il deploy (Render ha bisogno di tempo per inizializzare il DB)
3. Prova ad accedere direttamente all'URL YOURLS

### Signature non valida

1. Rigenerazione su YOURLS (Tools → API)
2. Aggiorna su Render
3. Attendi 1 minuto per il riavvio

---

## 💾 File Necessari

```
amazon-affiliate-bot/
├── amazon_bot.py              # Bot principale
├── Dockerfile                 # Container per Render
├── requirements.txt           # Dipendenze
├── .env-example               # Template variabili
├── .gitignore
└── README.md                  # Questo file
```

---

## 🔐 Sicurezza

- ✅ Non inserire credenziali nel codice
- ✅ Usa variabili d'ambiente su Render
- ✅ Non committare `.env` su GitHub (usa `.env-example`)
- ✅ Cambia password di default in produzione

---

## 💬 Support

Problemi? Apri un **Issue** su GitHub!

---

**Ready to launch? 🚀**
