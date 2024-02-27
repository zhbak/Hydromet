FROM python:3.9-alpine
RUN mkdir /hydromet_bot
WORKDIR /hydromet_bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
