# Running

This starts the container, which spins up a web server that you can use to access the data via REST.

## Docker compose

To start using docker-compose, run:

`docker-compose up -d`

## Seed database

You can seed the database with an arXiv dump. For example, the [arXiv dump from Kaggle](https://www.kaggle.com/Cornell-University/arxiv) can be used. Place the downloaded file in the `./mongo-seed` folder, and name the file as `arxiv.json`.

Only run this command once, as running it multiple times results in duplicated data.

`docker-compose --profile seed up -d`

Importing the data can take a while. Follow the progress with `docker-compose logs --follow mongo-seed`

# Running the parsers

Running the parsers takes time, probably you want to keep running them even when the terminal sessions stops. E.g., you can use:

`nohup python parser-orkg-title-parser.py &`

# Additional parser tools

Two of the tools are accessed via external REST endpoints. For this you need to setup the services within the same docker network.

-   [AmbiverseNLU](https://github.com/ambiverse-nlu/ambiverse-nlu) (make runs it runs on `http://nlu:8080/`, which is the default). Run the service: `docker-compose -f docker-compose/service-postgres.yml up`
-   [ORKG annotation](https://gitlab.com/TIBHannover/orkg/annotation) (make sure it runs on `http://annotation:5000/annotator/`, which is the default)

# Running JSON to RDF mapper

Ensure you run GraphDB to insert the RDF statements: https://github.com/Ontotext-AD/graphdb-docker

By default, GraphDB is expected to run at `http://localhost:10085/` which a repository called `tiny-genius`. This can be changed in `mapper-json-to-rdf.py`
