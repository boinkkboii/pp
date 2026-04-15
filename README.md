# VGC Analyst 🏆

VGC Analyst is a comprehensive analytics platform for Pokémon VGC (Video Game Championships). It combines real-time tournament data, a sophisticated teambuilder with synergy analysis, a damage calculation microservice, and an AI-powered strategic advisor.

## 🌟 Features

- **Tournament Insights**: Track and analyze recent VGC tournament results.
- **Teambuilder**: Build your competitive team with built-in synergy charts and meta-analysis.
- **AI Strategic Advisor**: Chat with an AI agent trained on current VGC meta-data to improve your play.
- **Damage Calc Service**: High-speed damage calculations powered by a dedicated microservice.
- **Data Pipeline**: Automated scrapers and seeders to keep the database up-to-date with the latest meta.

---

## 🚀 Getting Started (Beginner Friendly)

This guide is designed for someone who has just cloned the repository and may not have a background in software development. Follow these steps in order.

### 1. Prerequisites

You need to install three main tools on your computer:

1.  **Python (3.10 or higher)**: [Download here](https://www.python.org/downloads/)
    - *Note: During installation on Windows, make sure to check the box "Add Python to PATH".*
2.  **Node.js (18 or higher)**: [Download here](https://nodejs.org/)
3.  **MySQL Server**: [Download here](https://dev.mysql.com/downloads/installer/)
    - Create a database named `vgc_db` after installation.

---

### 2. Setup the Environment

#### A. Create your Configuration File
1.  In the main folder, find a file named `.env.example`.
2.  Create a copy of it and rename the copy to `.env`.
3.  Open `.env` in a text editor (like Notepad) and:
    - Set `DB_PASSWORD` to your MySQL password.
    - If you have a Google Gemini API Key, paste it into `GEMINI_API_KEY`.

#### B. Setup the Backend (Python)
1.  Open your terminal or command prompt in the main folder.
2.  Create a "virtual environment" (a private space for this project's tools):
    ```bash
    python -m venv venv
    ```
3.  Activate it:
    - **Windows**: `venv\Scripts\activate`
    - **Mac/Linux**: `source venv/bin/activate`
4.  Install the required Python tools:
    ```bash
    pip install -r requirements.txt
    ```

#### C. Setup the Calculation Service (Node.js)
1.  Navigate into the `calc_service` folder: `cd calc_service`
2.  Install the tools: `npm install`
3.  Go back to the main folder: `cd ..`

#### D. Setup the Frontend (React)
1.  Navigate into the `frontend` folder: `cd frontend`
2.  Install the tools: `npm install`
3.  Go back to the main folder: `cd ..`

---

### 3. Initialize the Database

Before running the app, you need to set up the tables and add some data.

1.  **Run Database Migrations** (Creates the tables):
    
    alembic revision --autogenerate
    alembic upgrade head

2.  **Seed Pokemon Data** (Populates the database with initial Pokémon data):
    
    python -m data_pipeline.seeder

3.  **Seed Tournament Data** (Populates the database with tournament data):
    
    python -m data_pipeline.main
    
---

### 4. Running the Application

To run the full platform, you need to start **three separate processes**. Open three different terminal windows:

**Window 1: The Backend (API)**
```bash
# Ensure venv is activated
uvicorn backend.main:app --reload
```

**Window 2: The Calculation Service**
```bash
cd calc_service
node index.js
```

**Window 3: The Frontend (Website)**
```bash
cd frontend
npm run dev
```

The website will now be available at **`http://localhost:5173`**. Open this in your browser!

---

## 🛠 Tech Stack

- **Frontend**: React 19, Vite, Recharts, React Router.
- **Backend**: FastAPI (Python), SQLAlchemy ORM.
- **Database**: MySQL.
- **AI**: Google Gemini Pro (via `google-genai`).
- **Calc Engine**: Node.js microservice.

## 🤝 Contributing

This project is a work in progress. Feel free to open issues or submit pull requests to improve the VGC meta-analysis tools!

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
