FROM mongo

COPY arxiv.json /arxiv.json
CMD mongoimport --host mongodb_container --db tinyGenius --collection papers --type json --file /arxiv.json --password rootpassword --authenticationDatabase admin -u root