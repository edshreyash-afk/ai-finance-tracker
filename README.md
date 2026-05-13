# AI Finance Tracker

A smart, web-based personal finance application built with Python and Flask. This tracker allows users to manage their daily transactions, categorize expenses, and receive intelligent insights and budgeting advice based on their spending habits.

## 🌟 Features

- **User Authentication:** Secure registration and login system.
- **Transaction Management:** Add, edit, and delete income and expenses easily.
- **Dashboard Overview:** Get a quick glance at your total balance, monthly income, and expenses.
- **AI-Powered Insights:** Conversational, personalized financial advice driven by the Google Gemini API, including:
  - Context-aware spending behavior analysis
  - Actionable savings recommendations
  - Dynamic financial health evaluation
- **Data Export:** Export your transaction history to CSV for external use.
- **Responsive UI:** Clean and modern interface built with Bootstrap 5.

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLAlchemy (SQLite by default, configurable via environment variables)
- **AI Engine:** Google Gemini API (google-generativeai)
- **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2 Templates


## 📂 Project Structure

```
ai-finance-tracker/
├── ai/                 # Logic for financial insights and data analysis
├── routes/             # Flask blueprints for routing (auth, dashboard, etc.)
├── static/             # CSS, JavaScript, and images
├── templates/          # Jinja2 HTML templates
├── app.py              # Application entry point
├── config.py           # Configuration handling
├── models.py           # SQLAlchemy database models
└── requirements.txt    # Python dependencies
```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! 
Feel free to check the [issues page](https://github.com/edshreyash-afk/ai-finance-tracker/issues) if you want to contribute.

---
*Built to help you track smarter, not harder.*
