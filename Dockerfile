FROM python

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN apt-get update && apt-get install nodejs npm -y
RUN npm install

RUN useradd app --uid 1000
USER app

CMD [ "python", "app.py"]