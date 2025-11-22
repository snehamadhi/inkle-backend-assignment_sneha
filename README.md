Inkle Backend Assignment — Sneha

This backend project implements a social platform system with authentication, posts, following, blocking, likes, admin roles, and activity feed logging.

 Live Deployment

🔗 https://inkle-backend-assignment-sneha.onrender.com

Use /docs for Swagger UI.

📌 Features

JWT Authentication (Signup/Login)

Create & Delete Posts

Like/Unlike Posts

Follow/Unfollow Users

Block/Unblock Users

Global Activity Feed

Owner/Admin permissions

Fully deployed on Render

Postman Collection

Available in repo as:

postman_collection.json

🛠 Tech Stack
Component	Tool
Backend Framework	FastAPI
Database	SQLite + SQLAlchemy ORM
Auth	JWT (python-jose)
Deployment	Render
🧪 Testing

All endpoints tested using:

Postman

Hoppscotch


📂 Project Structure
app/
 ┣ routers/
 ┣ models.py
 ┣ schemas.py
 ┣ security.py
 ┣ database.py
 ┣ dependencies.py
main.py
requirements.txt
Procfile

🏁 Final Notes

This project follows clean architecture, modular routing, role-based access control, and includes complete documentation.
