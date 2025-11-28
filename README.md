🏡 Real Estate Analytics Chatbot

A full-stack application that allows users to query real estate insights such as price trends, demand trends, and area-wise comparisons using a natural language chat interface.

🚀 Tech Stack
Backend

Python

Django & Django REST Framework

Pandas & NumPy (Excel-based analytics)

CORS enabled for frontend communication

Frontend

React (TypeScript)

Tailwind CSS

Recharts (for dynamic graphs)

Dataset

Excel dataset containing:

Final Location (Area), Year, City, Latitude, Longitude

Demand & sales metrics

Weighted average price and prevailing price ranges

Units / Carpet area supplied etc.

🔥 Features

✔ Natural language query engine
✔ Summaries for any supported location
✔ Dynamic charts (price vs demand over time)
✔ Area-to-area comparison mode
✔ Chat-style conversational interface
✔ Support for uploading custom Excel files (optional)

🧠 Sample Queries
Query Type	Example
Area Analysis	“Give me analysis of Wakad”
Comparison	“Compare Ambegaon Budruk and Aundh demand trends”
Price Growth	“Show price growth for Akurdi over the last 3 years”
General	“What does the data say about Aundh?”

Supported locations in dataset: Akurdi, Ambegaon Budruk, Aundh, Wakad

📁 Project Structure
realestate_chatbot/
│
├─ backend/
│  ├─ analysis/
│  │  ├─ utils.py      ← dataset processing & analytics
│  │  ├─ views.py      ← API endpoints
│  │  ├─ urls.py
│  ├─ realestate_chatbot/
│  │  ├─ settings.py
│  │  ├─ urls.py
│  ├─ datasets/
│  │  └─ realestate_data.xlsx
│  ├─ manage.py
│
├─ frontend/
│  ├─ src/
│  │  ├─ components/   ← Chat UI, AreaCard, CompareCard, Chart
│  │  ├─ pages/
│  │  ├─ App.tsx
│  │  ├─ main.tsx
│  ├─ index.html
│  ├─ tsconfig.json
│  ├─ vite.config.ts

🛠 Backend Setup (Local)
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

Test the API
POST /api/analysis/query/
Body:
{
  "query": "Analyze Wakad",
  "use_preloaded": true
}

🌐 Frontend Setup (Local)
cd frontend
npm install
npm run dev

Environment Variable

Create .env in frontend/:

VITE_API_BASE_URL=http://127.0.0.1:8000

☁ Deployment
Backend (Render)

Push backend to GitHub

Add Procfile:

web: gunicorn realestate_chatbot.wsgi:application --bind 0.0.0.0:$PORT


Deploy as Web Service → Python → Gunicorn

Frontend (Vercel)

Deploy frontend repo

Add environment variable:

VITE_API_BASE_URL=https://<your-render-service>.onrender.com

🧪 API Endpoints
Method	Endpoint	Purpose
POST	/api/analysis/query/	Run analysis using natural language
POST	/api/analysis/upload/	Upload custom Excel dataset (optional)
💬 How the Backend Works (Analytics Logic)

Reads Excel dataset

Normalizes column names

Identifies price & demand columns dynamically

Filters data by location

Computes:

Average market price

Demand / volume

Year-wise price curve

Percentage price change

Returns JSON summary + chart + table format

📌 To-Do / Future Enhancements

User authentication

Export summary as PDF

Admin panel for dataset management

🤝 Contributing

Pull requests are welcome. For feature requests or bug reports, open an issue.

📝 License

This project is for academic and research purposes.
