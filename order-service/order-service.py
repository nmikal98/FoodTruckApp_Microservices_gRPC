from concurrent import futures

import grpc
import order_pb2
import order_pb2_grpc

import time
import mysql.connector  


class Listener(order_pb2_grpc.orderServiceServicer):

    def order(self, request, context):
     
        try:
            conn = mysql.connector.connect(host = 'mydb_micro' , user = 'root' , passwd = 'Aa123456!' , database='foodtruckdb')  

            cursor = conn.cursor()

            cursor.execute('INSERT INTO orders VALUES (NULL, %s, %s, %s,%s, %s)', (request.sessId, request.truckname, request.location, request.orderDetails, request.date))
            
            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            print("Server made a boo boo")



        return order_pb2.orderResponse(status="success")
    


     
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


        return order_pb2.searchStoreResponse(trucks = results)



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    order_pb2_grpc.add_orderServiceServicer_to_server(Listener(), server)
    server.add_insecure_port("[::]:9998")
    server.start()
    try:
        while True:
            print("order service on" )
            time.sleep(10)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        server.stop(0)



if __name__ == '__main__':
    serve()