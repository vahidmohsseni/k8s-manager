FROM python:3.8.13-alpine

WORKDIR /api

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5001

ENTRYPOINT ["python3"]
CMD ["app.py"]
