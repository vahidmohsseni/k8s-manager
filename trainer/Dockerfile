FROM python:3.8.13-alpine

WORKDIR /trainer

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5002

ENTRYPOINT ["python3"]
CMD ["app.py"]
