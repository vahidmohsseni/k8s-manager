FROM python:3.8.13-alpine

WORKDIR /backend-service-manager

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5555
EXPOSE 5556

ENTRYPOINT ["python3"]
CMD ["service.py"]
