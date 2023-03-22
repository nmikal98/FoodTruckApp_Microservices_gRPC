from concurrent import futures
import grpc
import search_pb2
import search_pb2_grpc
import sys

from elasticsearch import Elasticsearch, exceptions
import time
import requests

import json



#es = Elasticsearch("http://localhost:9200")

es = Elasticsearch(host='es_micro')


################################################
# ElasticSearch Functions
################################################


def load_data_in_es():
    """ creates an index in elasticsearch """
   # url = "http://data.sfgov.org/resource/rqzj-sfat.json"
   # r = requests.get(url)
   # data = r.json()

    with open('./data.json', 'r') as f:
        json_data = f.read()

# Parse the JSON data into a Python object
    data = json.loads(json_data)

    print("Loading data in elasticsearch ...")
    for id, truck in enumerate(data):
        res = es.index(index="sfdata", id=id, body=truck)
    print("Total trucks loaded: ", len(data))

def safe_check_index(index, retry=3):
    """ connect to ES with retry """
    if not retry:
        print("Out of retries. Bailing out...")
        sys.exit(1)
    try:
        status = es.indices.exists(index=index)
        return status
    except exceptions.ConnectionError as e:
        print("Unable to connect to ES. Retrying in 5 secs...")
        time.sleep(5)
        safe_check_index(index, retry-1)

def format_fooditems(string):
    items = [x.strip().lower() for x in string.split(":")]
    return items[1:] if items[0].find("cold truck") > -1 else items

def check_and_load_index():
    """ checks if index exits and loads the data accordingly """
    if not safe_check_index('sfdata'):
        print("Index not found...")
        load_data_in_es()



class Listener(search_pb2_grpc.searchServiceServicer):
    def __init__(self, *args, **kwargs):
        self.key = ""


    def Search(self, request, context):
     
        try:
            res = es.search(
                index="sfdata",
                body={
                    "query": {"match": {"fooditems": request.req}},
                    "size": 750  # max document size
                })
        except Exception as e:
            print("Server made a boo boo")

        # filtering results
        vendors = set([x["_source"]["applicant"] for x in res["hits"]["hits"]])
        temp = {v: [] for v in vendors}
        fooditems = {v: "" for v in vendors}
        for r in res["hits"]["hits"]:
            applicant = r["_source"]["applicant"]
            if "location" in r["_source"]:
                truck = {
                    "hours": r["_source"].get("dayshours", "NA"),
                    "schedule": r["_source"].get("schedule", "NA"),
                    "address": r["_source"].get("address", "NA"),
                    "location": r["_source"]["location"]
                }
                fooditems[applicant] = r["_source"]["fooditems"]
                temp[applicant].append(truck)

        # building up results
        results = []
        for v in temp:
            results.append({
                "name": v,
                "fooditems": format_fooditems(fooditems[v]),
                "branches": temp[v],
                "drinks": fooditems[v].find("COLD TRUCK") > -1
            })
        hits = len(results)
        locations = sum([len(r["branches"]) for r in results])


        return search_pb2.searchResponse(trucks = results, hits = hits, locations = locations, status="success")
    

    def SearchStore(self, request, context):
     
        try:
            res = es.search(
                index="sfdata",
                body={
                    "query": {"match_phrase": {"applicant": request.req}},
                    "size": 750  # max document size
                })
        except Exception as e:
            print("Server made a boo boo")

        # filtering results
        vendors = set([x["_source"]["applicant"] for x in res["hits"]["hits"]])
        temp = {v: [] for v in vendors}
        fooditems = {v: "" for v in vendors}
        for r in res["hits"]["hits"]:
            applicant = r["_source"]["applicant"]
            if "location" in r["_source"]:
                truck = {
                    "hours": r["_source"].get("dayshours", "NA"),
                    "schedule": r["_source"].get("schedule", "NA"),
                    "address": r["_source"].get("address", "NA"),
                    "location": r["_source"]["location"]
                }
                fooditems[applicant] = r["_source"]["fooditems"]
                temp[applicant].append(truck)

        # building up results
        results = []
        for v in temp:
            results.append({
                "name": v,
                "fooditems": format_fooditems(fooditems[v]),
                "branches": temp[v],
                "drinks": fooditems[v].find("COLD TRUCK") > -1
            })
        hits = len(results)
        locations = sum([len(r["branches"]) for r in results])


        return search_pb2.searchStoreResponse(trucks = results)



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    search_pb2_grpc.add_searchServiceServicer_to_server(Listener(), server)
    server.add_insecure_port("[::]:9999")
    server.start()
    try:
        while True:
            print("search service on" )
            time.sleep(10)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        server.stop(0)



if __name__ == '__main__':

    check_and_load_index()
    serve()