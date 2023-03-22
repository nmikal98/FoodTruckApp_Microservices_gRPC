from concurrent import futures
import grpc
import serve_pb2
import serve_pb2_grpc
import time
import mysql.connector
from grpc import StatusCode

class Listener(serve_pb2_grpc.serveServiceServicer):
    def serve(self, request, context):
        try:
            conn = mysql.connector.connect(host='mydb_micro', user='root', passwd='Aa123456!', database='foodtruckdb')
            cursor = conn.cursor()
            cursor.execute('UPDATE orders SET isCompleted = 1 WHERE id =%s;', (request.order, ))
            conn.commit()

            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()

            if affected_rows == 0:
                return serve_pb2.serveResponse(status="Order not found")
            else:
                return serve_pb2.serveResponse(status="success")

        except Exception as e:
            print("Server made a boo boo:", e)
            context.set_code(StatusCode.INTERNAL)
            context.set_details('An error occurred while updating the order')
            return serve_pb2.serveResponse(status="failed")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    serve_pb2_grpc.add_serveServiceServicer_to_server(Listener(), server)
    server.add_insecure_port("[::]:9997")
    server.start()
    try:
        while True:
            print("serve service on")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        server.stop(0)

if __name__ == '__main__':
    serve()
