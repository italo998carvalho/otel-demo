run-server:
	@echo "Running server..."
	source venv/bin/activate && python3 server/run.py

run-client:
	@echo "Running client..."
	source venv/bin/activate && python3 client/run.py
