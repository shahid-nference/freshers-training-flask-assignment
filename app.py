import pymongo
from flask import Flask, request
from pymongo.mongo_client import MongoClient
import requests
import json

app = Flask(__name__)
app.debug = True

APPLICATION_HOST = "localhost"
APPLICATION_PORT = 24537

# Insert ur mongo user credetials here
MONGO_USER = ""
MONGO_PASSWORD = ""
MONGO_HOST = "mongo.servers.nferx.com"

DATABASE = "shahid"
PROJECTS_COLLECTION = "projects"
DATASETS_COLLECTION = "datasets"
MODELS_COLLECTION = "models"

PROJECT_SERVICE_API = "http://sentenceapi2.servers.nferx.com:8015/tagrecorder/v3/projects/"

MONGO_CLIENT = pymongo.MongoClient("mongodb://{}:{}@{}".format(MONGO_USER,MONGO_PASSWORD,MONGO_HOST))


@app.route("/healthcheck",methods=["GET"])
def healthcheck():
    return {
        "status" : "available"
    }

@app.route("/",methods=["GET"])
def rootpage():
    return {
        "Project" : "Mongo-Flask Assignment",
        "Name" : "Shahid"
    }

@app.route("/import_project",methods=["POST"])
def import_project():
    params = {}
    project_id = request.args.get("project_id","")
    response = json.loads(requests.get(PROJECT_SERVICE_API + str(project_id), params=params).text)
    
    if not response["success"] : 
        return {
            "success" : False,
            "message" : "project doesn't exist OR Unable to fetch project details."
        }

    # projects collection in my db
    my_projects_collection = MONGO_CLIENT[DATABASE][PROJECTS_COLLECTION]

    query_res = my_projects_collection.find({"_id" : project_id})
    query_res = list(query_res)
    if  len(query_res) != 0 and query_res[0]["last_updated"] == response["result"]["project"]["last_updated"]:
        return {
            "success" : True,
            "message" : "Given project is already in my database and up-to-date. No update is required as well!"
        }

    # datasets_list_with_info is a [] of {}. each {} has one dataset info. similarly for models_list_with_info
    datasets_list_with_info = response["result"]["project"]["associated_datasets"]
    models_list_with_info = response["result"]["project"]["models"]
    
    datasets_list = []
    for dataset in datasets_list_with_info :
        _dataset = {}
        _dataset["_id"] = dataset["_id"]
        _dataset["name"] = dataset["name"]
        datasets_list.append(_dataset)
    
    response["result"]["project"]["associated_datasets"] = datasets_list
    
    models_list = []
    for model in models_list_with_info :
        models_list.append(model["model_name"])

    response["result"]["project"]["models"] = models_list

    res = my_projects_collection.update_one({"_id" : project_id}, {"$set" : response["result"]["project"]}, upsert=True)
    assert res.acknowledged

    # datasets collection in my db
    my_datasets_collection = MONGO_CLIENT[DATABASE][DATASETS_COLLECTION]

    # models collection in my db
    my_models_collection = MONGO_CLIENT[DATABASE][MODELS_COLLECTION]

    # Add new datasets to datsets collections
    for dataset in datasets_list_with_info :
        dataset_id = dataset["_id"]
        res = my_datasets_collection.update_one({"_id" : dataset_id}, {"$set" : dataset}, upsert=True)
        assert res.acknowledged

    for model in models_list_with_info :
        model_name = model["model_name"]
        res = my_models_collection.update_one({"model_name" : model_name}, { "$set" : model}, upsert=True)
        assert res.acknowledged

    response_message = ""

    if len(query_res) == 0 :
        response_message = "Project details added to my database."
    else :
        response_message = "Project already exists in my database. Updated with latest response from service endpoint."

    return {
        "success" : True,
        "message" : response_message
    }


@app.route("/get_project_related_datasets_models",methods = ["GET"])
def get_project_related_datasets_models():
    project_id = request.args.get("project_id","")
    my_projects_collection = MONGO_CLIENT[DATABASE][PROJECTS_COLLECTION]
    res = list(my_projects_collection.find({"_id" : project_id},{"_id" : 0, "associated_datasets" : 1, "models" : 1}))
    if len(res) == 0 :
        # if project with requested project_id is not present in my database, hit import_project API to update my database 
        
        params = {
            "project_id" : project_id
        }
        # making post call to import_project API
        response = json.loads(requests.post(url="http://{}:{}/import_project".format(APPLICATION_HOST, APPLICATION_PORT), params = params).text)
        
        if not response["success"] :
            return {
                "success" : True,
                "message" : "This project does not exist"
            }
        res = list(my_projects_collection.find({"_id" : project_id},{"_id" : 0, "associated_datasets" : 1, "models" : 1}))
    
    return {
        "success" : True,
        "result" : res[0]
    }

@app.route("/get_info", methods = ["GET"])
def get_info():
    info_of = request.args.get("info_of")
    id = request.args.get("id")

    my_collection = MONGO_CLIENT[DATABASE][info_of]
    res = []
    if info_of == "models" :
        res = list(my_collection.find({"model_name" : id}))
    elif info_of == "datasets" :
        res = list(my_collection.find({"_id" : id}))
    elif info_of == "projects" :
        res = list(my_collection.find({"_id" : id}))
        if len(res) == 0 :
            # if project with requested project_id is not present in my database, hit import_project API to update my database 
            params = {
                "project_id" : id
            }
            # making post call to import_project API
            response = json.loads(requests.post(url="http://{}:{}/import_project".format(APPLICATION_HOST, APPLICATION_PORT), params = params).text)
        
            if not response["success"] :
                return {
                    "success" : True,
                    "message" : "Requested project/model/dataset does not exist in the database."
                }
            res = list(my_collection.find({"_id" : id}))
    
    if len(res) == 0 :
        return {
            "success" : True,
            "message" : "Requested project/model/dataset does not exist in the database.",
        }
    res[0]["_id"] = str(res[0]["_id"])
    return {
        "success" : True,
        "message" : "Fetched info successfully.",
        "result" : res[0]
    }

@app.route("/get_models_trained_with_dataset", methods = ["GET"])
def get_models_trained_with_dataset() :
    dataset_id = request.args.get("dataset_id")
    my_models_collection = MONGO_CLIENT[DATABASE][MODELS_COLLECTION]
    res = list(my_models_collection.find({"datasets_used.dataset_id" : dataset_id},{"_id" : 0, "model_name" : 1}))
    return {
        "success" : True,
        "message" : "Fetched info successfully.",
        "result" : res
    }

if __name__ == "__main__":
    app.run(host=APPLICATION_HOST,port=APPLICATION_PORT)

