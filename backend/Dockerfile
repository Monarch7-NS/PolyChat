FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]