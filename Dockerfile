# TradingView MCP Server - Docker Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create logs directory
RUN mkdir -p logs

# Expose environment variable for API key
ENV ALPHA_VANTAGE_API_KEY=""

# Run the server
CMD ["python", "tradingview_mcp/server.py", "stdio"]
