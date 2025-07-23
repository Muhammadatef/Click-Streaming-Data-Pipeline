# Click Streaming Data Pipeline - Makefile

.PHONY: help start-services start-api start-generator run-spark health-check test clean clean-all

# Default target
help:
	@echo "🎯 Click Streaming Data Pipeline - Available Commands:"
	@echo ""
	@echo "📦 Infrastructure:"
	@echo "  make start-services    Start all Docker services"
	@echo "  make health-check      Check service health status"
	@echo ""
	@echo "🚀 Application:"
	@echo "  make start-api         Start the Flask API server"
	@echo "  make start-generator   Start the event data generator"
	@echo "  make run-spark         Run the Spark streaming job"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test              Run all tests"
	@echo "  make test-api          Test API server only"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean             Stop services and clean up"
	@echo "  make clean-all         Stop services and remove all data"
	@echo ""
	@echo "💡 Quick Start:"
	@echo "  1. make start-services"
	@echo "  2. make start-api      (in new terminal)"
	@echo "  3. make start-generator (in new terminal)"
	@echo "  4. make run-spark      (in new terminal)"

start-services:
	@echo "🚀 Starting all services..."
	@./scripts/start-services.sh

start-api:
	@echo "🔧 Starting API server..."
	@./scripts/start-api.sh

start-generator:
	@echo "📊 Starting data generator..."
	@./scripts/start-generator.sh

run-spark:
	@echo "⚡ Running Spark job..."
	@./scripts/run-spark-job.sh

health-check:
	@./scripts/health-check.sh

test:
	@echo "🧪 Running all tests..."
	@cd api && python -m pytest test/ -v
	@echo "✅ All tests completed"

test-api:
	@echo "🧪 Testing API server..."
	@cd api && python -m pytest test/ -v

clean:
	@echo "🧹 Cleaning up..."
	@./scripts/cleanup.sh

clean-all:
	@echo "🧹 Deep cleaning (removing all data)..."
	@./scripts/cleanup.sh --volumes

# Development targets
dev-setup:
	@echo "🔧 Setting up development environment..."
	@cd api && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@cd generator && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Development environment ready"

logs:
	@echo "📝 Showing service logs..."
	@docker compose logs -f

status:
	@echo "📊 Service status:"
	@docker compose ps