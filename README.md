# Running

This starts the container, which spins up a web server that you can use to access the data via REST.

## Docker compose

To start using docker-compose, run:

`docker-compose up -d`

## Seed database

You can seed the database with an arXiv dump. Only run this command once, as running it multiple times results in duplicated data.

`docker-compose --profile seed up -d`

Importing the data can take a while. Follow the progress with `docker-compose logs --follow mongo-seed`

# Running the parsers

Running the parsers takes time, probably you want to keep running them even when the terminal sessions stops. E.g., you can use:

`nohup python parser-orkg-title-parser.py &`
