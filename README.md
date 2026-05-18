# 🎯 Smart Price Tracker — Setup Guide

## 📁 Project Structure

```
price_tracker/
├── app.py              # Flask backend + scheduler
├── database.py         # SQLite CRUD operations
├── scraper.py          # Amazon & Flipkart price scraper
├── predictor.py        # ML price prediction (Linear Regression)
├── notifier.py         # SendGrid email alerts
├── requirements.txt    # Python dependencies
└── templates/
    └── index.html      # Dashboard UI
```

---

## ⚙️ Setup Instructions

### 1. Create & activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure SendGrid Email (for real alerts)

- Sign up at https://sendgrid.com (free tier: 100 emails/day)
- Create an API key in Settings → API Keys
- Verify a sender email in Settings → Sender Authentication

Set environment variables:
```bash
# Windows
set SENDGRID_API_KEY=your_api_key_here
set FROM_EMAIL=verified@yourdomain.com

# Mac/Linux
export SENDGRID_API_KEY=your_api_key_here
export FROM_EMAIL=verified@yourdomain.com
```

> ⚠️ Without the API key, alerts will just print to console (safe for testing).

### 4. Run the app
```bash
python app.py
```

Visit: http://localhost:5000

---

## 🚀 Features

| Feature | Details |
|---|---|
| Price Tracking | Amazon & Flipkart scraping |
| Auto Refresh | Every 30 minutes via APScheduler |
| Email Alerts | SendGrid (no personal password needed) |
| AI Prediction | Linear Regression on price history |
| Dashboard | Real-time UI with Chart.js graphs |
| Database | SQLite (persistent across restarts) |

---

## 💡 Tips

- **Best URLs**: Use product page URLs, not search results
- **Amazon**: Direct product links (amazon.in/dp/...) work best
- **Flipkart**: Direct product links work best
- **Testing**: Add a product with a very high target price to test email alerts immediately
- **Prediction**: Works after the product has at least 2 price records

---

## 🔧 Customization

- Change check interval in `app.py`: `minutes=30` → any value
- Add more e-commerce sites in `scraper.py`
- Modify email template in `notifier.py`
