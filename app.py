from flask import Flask, request, json, Response
from bson.json_util import loads, dumps
from bson.objectid import ObjectId
import requests
from flask_cors import CORS
from pymongo import MongoClient
from mongo import collection_papers, collection_properties, collection_resources

# init app & DB
app = Flask(__name__)
cors = CORS(app)

@app.route("/papers", methods=["GET"])
def read_all():
    # pagination
    page_size = 25
    page = int(request.args.get("page")) if request.args.get("page") is not None else 0
    skips = page_size * (page + 1 - 1)

    # filters
    filter = {}
    if request.args.get("title") is not None:
        filter["title"] = {"$eq": request.args.get("title")}
    if request.args.get("categories") is not None:
        filter["categories"] = {"$eq": request.args.get("categories")}

    documents = collection_papers.find(filter).skip(skips).limit(page_size)

    output = [
        {item: data[item] for item in data if item != "_id"} for data in documents
    ]
    return Response(
        response=json.dumps(output), status=200, mimetype="application/json"
    )


@app.route("/papers/<paper_id>", methods=["GET"])
def read(paper_id):
    data = request.json
    filter = {"id": paper_id}
    paper = collection_papers.find_one(filter)
    properties = []
    resources =[]

    if 'statements' in paper: 
        property_ids = []
        resource_ids = []
        for statement in paper["statements"]:
            property_ids.append(statement["property_id"])
            if "resource_id" in statement:
                resource_ids.append(statement["resource_id"])

        properties = collection_properties.find({"_id": {"$in": property_ids}})
        resources = collection_resources.find({"_id": {"$in": resource_ids}})

    return Response(
        response=dumps(
            {"paper": paper, "properties": properties, "resources": resources}
        ),
        status=200,
        mimetype="application/json",
    )

@app.route("/papers", methods=["POST"])
def create():
    data = request.json
    response = collection_papers.insert_one(data)
    output = {
        "Status": "Successfully Inserted",
        "Document_ID": str(response.inserted_id),
    }
    return Response(
        response=json.dumps(output), status=200, mimetype="application/json"
    )


@app.route("/papers/<paper_id>", methods=["PUT"])
def update(paper_id):
    data = request.json
    filter = {"id": paper_id}
    updated_data = {"$set": data}
    response = collection_papers.update_one(filter, updated_data)
    output = {
        "Status": "Successfully Updated"
        if response.modified_count > 0
        else "Nothing was updated."
    }

    return Response(
        response=json.dumps(output), status=200, mimetype="application/json"
    )


@app.route("/papers/<paper_id>", methods=["DELETE"])
def delete(paper_id):
    data = request.json
    filter = {"paper_id": paper_id}
    response = collection_papers.delete_one(filter)
    output = {
        "Status": "Successfully Deleted"
        if response.deleted_count > 0
        else "Document not found."
    }

    return Response(
        response=json.dumps(output), status=200, mimetype="application/json"
    )

@app.route("/papers/<paper_id>/statements/<statement_id>/votes", methods=["POST"])
def create_vote(paper_id, statement_id):
    data = request.json
    collection_papers.update(
        {
            "id": paper_id,
            "statements._id" : ObjectId(statement_id) 
        }, 
        { 
            "$push": { 
                "statements.$.votes": data
            } 
        }
    )

    return Response(response=dumps({}), status=200, mimetype="application/json")

@app.route("/resources/<resource_id>/papers", methods=["GET"])
def get_papers_by_resource_id(resource_id):
    data = request.json
    filter = {"statements.resource_id":  ObjectId(resource_id)}
    papers = collection_papers.find(filter, { "id": 1, "title": 1, "authors_parsed": 1, "abstract": 1, "update_date": 1 })
    
    return Response(
        response=dumps(
            papers
        ),
        status=200,
        mimetype="application/json",
    )

@app.route("/resources/<resource_id>", methods=["GET"])
def get_resource(resource_id):
    filter = {"_id": ObjectId(resource_id)}
    resource = collection_resources.find_one(filter)

    return Response(
        response=dumps(
            resource
        ),
        status=200,
        mimetype="application/json",
    )


@app.route("/papers-by-field", methods=["GET"])
def get_papers_by_field_without_nlp_data():
    field = request.args.get('field')

    filter = {
        "nlp_results": { "$exists": False },
        "categories": { "$regex" : f".*{field}.*" },
    }

    papers = collection_papers.find(filter, { "id": 1 })
    
    return Response(
        response=dumps(
            papers
        ),
        status=200,
        mimetype="application/json",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0", threaded=True)
