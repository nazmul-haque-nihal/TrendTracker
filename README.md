# 🔥 TrendTracker: Multi-Platform Trend Aggregator & Analyzer

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-blue.svg)](https://flask.palletsprojects.com/)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-1a1f2d?logo=render)](https://render.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A real-time dashboard for discovering the latest viral content across YouTube, Reddit, and more.**

[Live Demo (Backend API)](https://trendtracker-046o.onrender.com) | [Live Demo (Frontend Dashboard)](https://trendtracker-1.onrender.com)

</div>

---

## 🚀 Overview

TrendTracker is a web application designed to aggregate, analyze, and display trending content from multiple social media platforms. It leverages official APIs to fetch the latest short-form videos, clips, and posts, focusing on diverse categories such as *funny*, *emotional*, *anime*, *movie clips*, *viral music*, *viral dance*, and *technology*. The application features a responsive web dashboard for easy browsing and a robust backend scheduler for periodic data collection.

## ✨ Features

*   **Multi-Platform Scraping:** Fetches trending content from YouTube and Reddit (using official APIs).
*   **Categorized Content:** Videos/posts are categorized (e.g., funny, sad, anime, movie clips) for easy filtering.
*   **Global Focus:** Searches for popular content worldwide, with relevance to viewers potentially in Bangladesh (based on historical configuration).
*   **Short-Form Emphasis:** Prioritizes videos and clips under 12 minutes for quick consumption.
*   **Engagement Metrics:** Displays view counts, likes, and comments where available.
*   **Responsive Dashboard:** A modern, user-friendly interface built with vanilla HTML/CSS/JS, accessible on desktop and mobile.
*   **Automatic Updates:** A background scheduler periodically scrapes new trends (configurable interval).
*   **API-Driven:** Clean RESTful API built with Flask for backend-frontend communication.
*   **Deployed on Render:** Easily scalable and managed cloud infrastructure.

## 🛠️ Tech Stack

### Backend
*   **Language:** [Python 3.11+](https://www.python.org/)
*   **Framework:** [Flask](https://flask.palletsprojects.com/)
*   **Database:** [SQLAlchemy](https://www.sqlalchemy.org/) (ORM), with PostgreSQL on Render.
*   **APIs:** [YouTube Data API v3](https://developers.google.com/youtube/v3), [Reddit API (PRAW)](https://praw.readthedocs.io/)
*   **Web Server:** [Gunicorn](https://gunicorn.org/)
*   **Scheduler:** [APScheduler](https://apscheduler.readthedocs.io/)
*   **HTTP Client:** [Requests](https://requests.readthedocs.io/)

### Frontend
*   **Structure:** HTML5
*   **Styling:** CSS3 (with Flexbox/Grid for responsiveness)
*   **Logic:** Vanilla JavaScript (ES6+)
*   **API Interaction:** Fetch API

### Deployment
*   **Platform:** [Render](https://render.com)
*   **Database (Render):** PostgreSQL (Free Tier)

## 📁 Project Structure
 ```bash
trendtracker/
├── app.py                 # Main Flask application factory and Gunicorn entry point
├── init_db.py             # Script to initialize the database schema
├── requirements.txt       # Python dependencies
├── .env (Local)           # Environment variables (not in repo, use .env.example)
├── .gitignore
├── render.yaml            # Render deployment configuration
├── backend/
│   ├── __init__.py        # Initializes the SQLAlchemy instance
│   ├── config.py          # Application configuration and API key loading
│   ├── models/
│   │   ├── __init__.py
│   │   └── trend_model.py # SQLAlchemy model for Trend data
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── scraper_manager.py # Orchestrates different scrapers
│   │   ├── youtube_scraper.py # Fetches YouTube trends
│   │   └── reddit_scraper.py  # Fetches Reddit trends
│   └── api/
│       ├── __init__.py
│       └── routes.py      # Defines API endpoints (/api/trends, /api/scrape, etc.)
└── frontend/
    ├── index.html         # Main dashboard page
    ├── settings.html      # Configuration page (placeholder for API keys)
    ├── css/
    │   └── styles.css     # Frontend styling
    └── js/
        ├── app.js         # Core dashboard logic (fetching, displaying trends)
        ├── components.js  # UI component logic (filters)
        └── settings.js    # Settings page logic
 ```

## 🚀 Getting Started

### Prerequisites

*   Python 3.11+
*   Git
*   API Keys:
    *   YouTube Data API v3 Key
    *   Reddit App Client ID & Secret

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/nazmul-haque-nihal/TrendTracker.git
    cd TrendTracker
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    *   Create a `.env` file in the project root.
    *   Add your API keys:
        ```env
        FLASK_APP=app.py
        FLASK_ENV=development
        SECRET_KEY=your_very_secret_key_here
        DATABASE_URL=sqlite:///trendtracker.db # For local dev
        YOUTUBE_API_KEY=your_youtube_api_key
        REDDIT_CLIENT_ID=your_reddit_client_id
        REDDIT_CLIENT_SECRET=your_reddit_secret
        # FRONTEND_URL=http://localhost:8000 # For CORS if running frontend separately
        ```
    *   Ensure `DATABASE_URL` points to a local SQLite file (`sqlite:///trendtracker.db`) for local development.

5.  **Initialize the database:**
    ```bash
    python init_db.py
    ```

6.  **Start the backend server:**
    ```bash
    python app.py
    # Backend API will be available at http://localhost:5000
    ```

7.  **(Optional) Serve the frontend locally:**
    *   In a new terminal, navigate to the `frontend` directory:
        ```bash
        cd frontend
        python -m http.server 8000
        # Frontend will be available at http://localhost:8000
        ```
    *   Note: You might need to adjust the `API_BASE_URL` in `frontend/js/app.js` to `http://localhost:5000` for local communication.

### Deployment on Render

1.  **Fork/Clone** this repository to your GitHub account.
2.  **Create a new Web Service** on [Render](https://dashboard.render.com/).
3.  **Connect your GitHub repository.**
4.  **Configure the build and start commands:**
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn app:app`
    *   **Environment:** `Python`
5.  **Add Environment Variables** in the Render dashboard for your service:
    *   `SECRET_KEY`
    *   `YOUTUBE_API_KEY`
    *   `REDDIT_CLIENT_ID`
    *   `REDDIT_CLIENT_SECRET`
    *   `FRONTEND_URL` (Set this to your Render Static Site URL, e.g., `https://trendtracker-1.onrender.com`)
6.  **Create a linked PostgreSQL Database** via Render's dashboard and link it to your Web Service (Render automatically sets `DATABASE_URL`).
7.  **Deploy!** Render will build, install dependencies, and start your application automatically.

## 🔧 Configuration

### API Keys

The application relies on API keys for external platforms. These are loaded from environment variables as defined in `backend/config.py`. Ensure they are correctly set in your deployment environment (Render dashboard) or `.env` file for local development.

### Scheduler

Automatic scraping is handled by `APScheduler` in `app.py`. The interval is currently set to run every 6 hours. You can adjust this by modifying the `hours=6` parameter in the `scheduler.add_job` call within `app.py`.

### CORS

CORS is configured in `app.py` using `Flask-CORS`. It allows requests from the `FRONTEND_URL` environment variable and `http://localhost:8000` by default. Ensure the `FRONTEND_URL` environment variable is set correctly on Render.

## 📊 API Endpoints

*   `GET /api/trends?platform=...&category=...&limit=...`: Fetches paginated trends based on filters.
*   `POST /api/scrape`: Triggers the scraping process for enabled platforms.
*   `GET /api/config`: Retrieves application configuration (enabled platforms).

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you would like to change, or feel free to tackle any existing issues. Fork the repository, make your changes, and submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🧑‍💻 Author

[nazmul-haque-nihal](https://github.com/nazmul-haque-nihal)

---
<div align="center">
Made with ❤️ using Python, Flask, and Render.
</div>
