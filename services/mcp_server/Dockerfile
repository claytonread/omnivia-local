FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY services/mcp_server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/mcp_server/ /app/services/mcp_server/

# MCP server communicates via stdio, no port needed
CMD ["python", "-m", "services.mcp_server.server"]