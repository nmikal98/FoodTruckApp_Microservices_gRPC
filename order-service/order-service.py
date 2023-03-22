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

            cursor.execute('INSERT INTO orders VALUES (NULL, %s, %s, %s,%s, %s, %s)', (request.sessId, request.truckname, request.location, request.orderDetails, request.date, 0))
            
            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            print("Server made a boo boo")



        return order_pb2.orderResponse(status="success")
    





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