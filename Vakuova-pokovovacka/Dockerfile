FROM python:3.11-slim
WORKDIR /main

COPY Vakuova-pokovovacka/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY Vakuova-pokovovacka/ . 

CMD ["python", "-u", "main.py"]