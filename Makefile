.PHONY: setup backend frontend test test-backend test-frontend build clean docker

# One-command full setup
setup: setup-backend setup-frontend
	@echo ""
	@echo "Setup complete! Run 'make dev' to start both servers."
	@echo ""

setup-backend:
	@echo "Setting up backend..."
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; echo "Created backend/.env from .env.example"; fi

setup-frontend:
	@echo "Setting up frontend..."
	cd frontend && npm install

# Start development servers
dev:
	@echo "Starting backend on :8000 and frontend on :5173..."
	@echo "Press Ctrl+C to stop."
	@make -j2 backend frontend

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

# Run all tests
test: test-backend test-frontend
	@echo ""
	@echo "All tests passed!"

test-backend:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npx vitest run

# Production build
build:
	cd frontend && npm run build

# Docker
docker:
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; echo "Created backend/.env from .env.example"; fi
	docker-compose up --build

docker-down:
	docker-compose down

# Clean generated files
clean:
	rm -rf backend/__pycache__ backend/app/__pycache__ backend/.pytest_cache
	rm -rf backend/tests/__pycache__ backend/meetingmind.db backend/test_meetingmind.db
	rm -rf frontend/node_modules frontend/dist
