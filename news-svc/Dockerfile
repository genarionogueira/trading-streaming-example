FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime dependencies (keep it minimal)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi "uvicorn[standard]" strawberry-graphql

# Copy application source
COPY src ./src

EXPOSE 4000

# Run the ASGI app; point uvicorn at the src dir
CMD ["uvicorn", "--app-dir", "src", "news_svc.server:app", "--host", "0.0.0.0", "--port", "4000"]