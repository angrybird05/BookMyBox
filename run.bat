@echo off
echo Starting BookMyBox Application...

echo Starting Backend (Docker Compose)...
cd backend
start "BookMyBox Backend" cmd /k "docker-compose up --build"
cd ..

echo Starting Frontend (Vite)...
cd frontend
start "BookMyBox Frontend" cmd /k "npm install && npm run dev"
cd ..

echo Application startup scripts launched!
echo You can close this window. Please check the new terminal windows for the logs.
pause
