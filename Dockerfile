FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_PORT=8501

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE ${STREAMLIT_PORT}

CMD streamlit run main.py --server.port=${STREAMLIT_PORT} --server.enableCORS=false
