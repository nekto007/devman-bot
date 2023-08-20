FROM python:3.10-alpine

WORKDIR /devman-bot
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY dvmn_api.py ./

ENTRYPOINT ["python"]
CMD ["dvmn_api.py"]