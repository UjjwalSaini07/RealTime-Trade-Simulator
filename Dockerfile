# Use official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_PORT=8501

# Set working directory
WORKDIR /app

# Copy requirement files
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose Streamlit default port
EXPOSE ${STREAMLIT_PORT}

# Run Streamlit
CMD streamlit run main.py --server.port=${STREAMLIT_PORT} --server.enableCORS=false
