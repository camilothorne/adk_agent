FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GOOGLE_GENAI_USE_VERTEXAI=TRUE

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY query_companion/ ./query_companion/
COPY utils/ ./utils/

EXPOSE 8080

CMD ["sh", "-c", "exec adk web --host 0.0.0.0 --port ${PORT:-8080}"]