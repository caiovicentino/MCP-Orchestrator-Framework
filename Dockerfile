FROM python:3.9-slim

WORKDIR /app

# Copy the package files
COPY setup.py README.md ./
COPY mcp_orchestrator ./mcp_orchestrator
COPY examples ./examples

# Install the package
RUN pip install --no-cache-dir -e .

# Set the entrypoint to run the example
ENTRYPOINT ["python", "examples/example_usage.py"]
