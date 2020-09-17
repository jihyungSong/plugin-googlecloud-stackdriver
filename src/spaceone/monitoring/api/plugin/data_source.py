from spaceone.api.monitoring.plugin import data_source_pb2, data_source_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class DataSource(BaseAPI, data_source_pb2_grpc.DataSourceServicer):

    pb2 = data_source_pb2
    pb2_grpc = data_source_pb2_grpc

    def verify(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('DataSourceService', metadata) as data_source_svc:
            response_stream = data_source_svc.verify(params)
            for response in response_stream:
                yield self.locator.get_info('PluginVerifyResponse', response)