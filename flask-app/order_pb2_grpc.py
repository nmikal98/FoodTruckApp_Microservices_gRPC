# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import order_pb2 as order__pb2


class orderServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.order = channel.unary_unary(
                '/orderService/order',
                request_serializer=order__pb2.orderRequest.SerializeToString,
                response_deserializer=order__pb2.orderResponse.FromString,
                )


class orderServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def order(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_orderServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'order': grpc.unary_unary_rpc_method_handler(
                    servicer.order,
                    request_deserializer=order__pb2.orderRequest.FromString,
                    response_serializer=order__pb2.orderResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'orderService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class orderService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def order(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/orderService/order',
            order__pb2.orderRequest.SerializeToString,
            order__pb2.orderResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
