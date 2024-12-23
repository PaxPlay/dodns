FROM python:3.12

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./dodns.py ./

CMD ["python", "./dodns.py"]

