FROM python

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN apt-get update && apt-get install nodejs npm -y
RUN npm install

CMD [ "python", "app.py"]