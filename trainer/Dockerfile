FROM python:3.11-alpine

WORKDIR /trainer

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5002

ENTRYPOINT ["python3"]
CMD ["app.py"]
