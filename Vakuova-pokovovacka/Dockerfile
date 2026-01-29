FROM python:3.11-slim
WORKDIR /main

COPY Vakuova-pokovovacka/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/

COPY Vakuova-pokovovacka/components/ ./components/

COPY Vakuova-pokovovacka/main.py .

COPY Vakuova-pokovovacka/data.py .

COPY Vakuova-pokovovacka/components/brain.py .

COPY Vakuova-pokovovacka/components/machine.py .

COPY Vakuova-pokovovacka/components/output.py .


CMD ["python", "-u", "main.py"]