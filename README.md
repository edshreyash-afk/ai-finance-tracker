# AI Finance Tracker

A smart, web-based personal finance application built with Python and Flask. This tracker allows users to manage their daily transactions, categorize expenses, and receive intelligent insights and budgeting advice based on their spending habits.

## 🌟 Features

- **User Authentication:** Secure registration and login system.
- **Transaction Management:** Add, edit, and delete income and expenses easily.
- **Dashboard Overview:** Get a quick glance at your total balance, monthly income, and expenses.
- **Smart Insights:** Data-driven analysis of your spending patterns, including:
  - Savings rate calculation
  - High-spending category alerts
  - Personalized budgeting tips and health score
- **Data Export:** Export your transaction history to CSV for external use.
- **Responsive UI:** Clean and modern interface built with Bootstrap 5.

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLAlchemy (SQLite by default, configurable via environment variables)
- **Data Analysis:** Pandas, NumPy
- **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2 Templates

## 🚀 Getting Started

Follow these steps to set up the project locally on your machine.

### Prerequisites

- Python 3.8+ installed
- Git installed

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/edshreyash-afk/ai-finance-tracker.git
   cd ai-finance-tracker
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up Environment Variables:**
   Create a `.env` file in the root directory of the project and add the following:
   ```env
   SECRET_KEY=your_super_secret_key_here
   DATABASE_URL=sqlite:///finance.db
   ```
   *(Note: The `DATABASE_URL` is optional. If not provided, it will fallback to a default SQLite database.)*

6. **Run the Application:**
   ```bash
   python app.py
   ```
   The application will start running on `http://127.0.0.1:5000`.

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
