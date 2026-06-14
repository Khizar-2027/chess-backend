# Chess Platform

A full-stack real-time chess application built as a portfolio project.

🔗 **Live Demo:** https://khizar-chess.vercel.app

---

## Features

- JWT Authentication (register, login)
- Create and join games in real time
- Full legal move validation
- Click-to-move and drag-to-move
- Pawn promotion
- Real-time gameplay via WebSockets
- Timers with live countdown
- Game end detection — checkmate, resignation, timeout, stalemate, draw
- Game history with results on dashboard
- Responsive design — desktop and mobile

---

## Tech Stack

**Frontend**
- React, React Router, CSS Modules
- react-chessboard
- Axios
- Deployed on Vercel

**Backend**
- Django, Django REST Framework
- Django Channels (WebSockets)
- JWT Authentication
- Deployed on Render

**Database & Infrastructure**
- PostgreSQL (Render)
- Redis via Upstash (WebSocket channel layer)

---

## Local Development

**Backend**
```bash
git clone https://github.com/Khizar-2027/chess-backend
cd chess-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend**
```bash
git clone https://github.com/Khizar-2027/chess-frontend
cd chess-frontend
npm install
npm run dev
```

---

> ⚠️ Hosted on Render free tier — first load may take ~30 seconds to wake up.