FROM python:3.7 
# for now use Python 3.7, building goes much faster because several wheel packages are missing for higher python versions

RUN apt-get update -y && \
    apt-get install -y python3-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN pip install cso_classifier
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader stopwords
COPY . /app


ENTRYPOINT [ "python" ]

CMD [ "app.py", "--host=0.0.0.0" ]
