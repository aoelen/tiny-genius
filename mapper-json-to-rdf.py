from SPARQLWrapper import SPARQLWrapper, JSON, POST
from mongo import collection_papers
from slugify import slugify
from datetime import datetime
import re

filter = {
    f"nlp_results": { "$exists": True },
    "$or": [
        {"processed":False},
        {"processed":{"$exists":False}}
    ]
}

while True:
    papers = list(collection_papers.find(filter).limit(1))

    paper_ids = []

    for paper in papers:
        title = paper['title'].replace("\n", " ")
        id = paper['id']
        abstract = paper['abstract'].replace("\n", " ").replace("\\", "")
        doi = paper['doi']
        update_date = paper['update_date']

        paper_ids.append(id)


        # authors
        authors = ""
        for author in paper['authors_parsed']:
            authors = f'dcterms:creator [ foaf:name "{author[0]}, {author[1]}" ] ;'

        #title parser
        title_parser = ''
        if 'orkg_title_parser' in paper['nlp_results']:
            entityToProperty = {
                'research_problem': ':researchProblem',
                'solution': ':solution',
                'resource': ':resource',
                'language': ':language',
                'tool': ':tool',
                'method': ':method',
            }

            for type in paper['nlp_results']['orkg_title_parser']:
                for entity in paper['nlp_results']['orkg_title_parser'][type]:
                    title_parser += f':{id} {entityToProperty[type]} :{slugify(entity, separator="_")} . \n'
                    title_parser += f':{slugify(entity, separator="_")} rdfs:label """{entity}""" . \n'
                    #matching_string = re.finditer(entity, title, re.IGNORECASE).__next__() # info not provided by tool, so determine on the fly
                    start_offset = paper['title'].find(entity)
                    index_matching = ''
                    if start_offset != -1:
                        index_matching = f"""nif:beginIndex "{start_offset}"^^xsd:int ;
                        nif:endIndex "{start_offset + len(entity)}"^^xsd:int ;"""

                    title_parser += f"""<<:{id} {entityToProperty[type]} :{slugify(entity, separator="_")}>> 
                    dc:creator :orkg_title_parser ;
                    dc:created "{datetime.now()}"^^xsd:dateTime ;
                    :hasTextReference [
                        nif:anchorOf \"\"\"{entity}\"\"\" ;
                        {index_matching}
                    ] . \n"""

        # cso classifier
        cso_classifier = ''
        if 'cso_classifier' in paper['nlp_results']:
            for entity in paper['nlp_results']['cso_classifier']['enhanced']:
                regex_pattern = r'[^-a-z0-9_]+'
                statement = f':{id} :hasTopic cso:{slugify(entity, separator="_", regex_pattern=regex_pattern)}'
                cso_classifier += f'{statement} . \n'

                text_references = ''
                explanations = paper['nlp_results']['cso_classifier']['explanation'][entity]
                if explanations:
                    for explanation in explanations:
                        start_offset = abstract.find(explanation)
                        if start_offset != -1:
                            text_references += f"""
                            :hasTextReference [
                                nif:anchorOf \"\"\"{explanation}\"\"\" ;
                                nif:beginIndex "{start_offset}"^^xsd:int ;
                                nif:endIndex "{start_offset + len(explanation)}"^^xsd:int ;
                            ] ;
                            """

                cso_classifier += f"""<<{statement}>> 
                    dc:creator :cso_classifier ;
                    {text_references}
                    dc:created "{datetime.now()}"^^xsd:dateTime . \n"""

        # abstract annotator
        abstract_annotator = ''
        if 'abstract_annotator' in paper['nlp_results']:
            entityToProperty = {
                'Data': ':hasData',
                'Process': ':hasProcess',
                'Material': ':hasMaterial',
                'Method': ':hasMethod',
            }

            for entity in paper['nlp_results']['abstract_annotator']:
                type = entity[1]
                offset_start = entity[2][0][0]
                offset_end = entity[2][0][1]
                confidence_level = entity[3]
                word = paper['abstract'][offset_start:offset_end].replace("\n", " ").replace("\\", "")
                statement = f':{id} {entityToProperty[type]} :{slugify(word, separator="_")}'
                abstract_annotator += f'{statement} . \n'
                abstract_annotator += f""":{slugify(word, separator="_")} rdfs:label \"\"\"{word}\"\"\" . \n"""

                abstract_annotator += f"""<<{statement}>> 
                dc:creator :abstract_annotator ;
                dc:created "{datetime.now()}"^^xsd:dateTime ;
                :hasTextReference [
                    nif:anchorOf \"\"\"{word}\"\"\" ;
                    nif:beginIndex "{offset_start}"^^xsd:int ;
                    nif:endIndex "{offset_end}"^^xsd:int ;
                    nif:confidence "{confidence_level}"^^xsd:decimal ;
                ] . \n"""

        # abstract annotator
        ambiverse_nlu = ''
        if 'ambiverse_nlu' in paper['nlp_results']:
            entityToProperty = {
                'Data': ':hasData',
                'Process': ':hasProcess',
                'Material': ':hasMaterial',
                'Method': ':hasMethod',
            }

            if 'entities' in paper['nlp_results']['ambiverse_nlu']:
                for entity in paper['nlp_results']['ambiverse_nlu']['entities']:
                    statement = f':{id} :mentionsConcept <{entity["id"]}>'
                    ambiverse_nlu += f'{statement} . \n'

                    text_maches = ''
                    for match in paper['nlp_results']['ambiverse_nlu']['matches']:
                        if 'id' in match['entity'] and match['entity']['id'] == entity['id']:
                            text_maches += f"""
                            :hasTextReference [
                                nif:anchorOf \"\"\"{match['text']}\"\"\" ;
                                nif:beginIndex "{match['charOffset']}"^^xsd:int ;
                                nif:endIndex "{match['charOffset'] + len(match['text'])}"^^xsd:int ;
                                nif:confidence "{match['entity']['confidence']}"^^xsd:decimal ;
                            ] ;
                            """

                    ambiverse_nlu += f"""<<{statement}>> 
                    dc:creator :ambiverse_nlu ;
                    {text_maches}
                    dc:created "{datetime.now()}"^^xsd:dateTime .
                    \n"""

        insert_triples = f"""
    PREFIX datacite: <http://purl.org/spar/datacite/>
    PREFIX fabio: <http://purl.org/spar/fabio/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX : <http://orkg.org/tiny-genius/>
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#>
    PREFIX arxiv: <https://arxiv.org/abs/>
    PREFIX cso: <https://cso.kmi.open.ac.uk/topics/>

    INSERT DATA
    {{ 
        :{id} dcterms:title \"\"\"{title}\"\"\" ;
                a fabio:Work ;
                dcterms:abstract \"\"\"{abstract}\"\"\" ;
                datacite:doi "{doi}" ;
                {authors}
                fabio:hasDisicipline :CS_LG ;
                fabio:dateLastUpdated "{update_date}"^^xsd:date ;
                arxiv:eprint "{id}" .
        
        {title_parser}
        {cso_classifier}
        {abstract_annotator}
        {ambiverse_nlu}
    }}
    """
        print(insert_triples)
        print(id)
        #try:
        sparql2 = SPARQLWrapper("http://localhost:10085/repositories/tiny-genius/statements")
        sparql2.setMethod(POST)
        sparql2.setReturnFormat(JSON)

        sparql2.setQuery(insert_triples)
        results = sparql2.query()
        # except Exception as e:
        #     print(e)

    collection_papers.update_many({"id":{"$in": paper_ids}}, {
        "$set": {
            "processed": True,
        }
    })