port-forward:
	@echo "Port forwarding boutique service to http://localhost:12345"
	kubectl port-forward --address=0.0.0.0 svc/boutique-de619ee0 12345:80

run-test:
	@if [ -z "$(DIR)" ]; then \
		echo "Usage: make run-test DIR=<directory_name>"; \
		echo "Example: make run-test DIR=monolith_run"; \
		exit 1; \
	fi
	@echo "Running load test with output directory: $(DIR)"
	@mkdir -p load-testing/results/$(DIR)
	locust -f load-testing/locustfile.py --host http://localhost:12345 --headless -u 200 -r 30 -t 15m --csv load-testing/results/$(DIR)/run_stats.csv --csv-full-history load-testing/results/$(DIR)/run_stats_history.csv

# Convenience targets for common test scenarios
run-test-monolith:
	$(MAKE) run-test DIR=monolith_run

run-test-microservices:
	$(MAKE) run-test DIR=microservices_run

help:
	@echo "Available targets:"
	@echo "  run-test DIR=<name>     - Run load test with custom output directory"
	@echo "  run-test-monolith       - Run test for monolith (outputs to monolith_run/)"
	@echo "  run-test-microservices  - Run test for microservices (outputs to microservices_run/)"
	@echo "  port-forward            - Forward boutique service to localhost:12345"
	@echo "  help                    - Show this help message"