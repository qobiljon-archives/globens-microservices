import grpc
import json

# import the generated classes
from gb_grpcs import gb_service_pb2
from gb_grpcs import gb_service_pb2_grpc

# open a gRPC channel
channel = grpc.insecure_channel('165.246.42.172:50051')

# create a stub (client)
stub = gb_service_pb2_grpc.GlobensServiceStub(channel)

if __name__ == '__main__':
    req = gb_service_pb2.FetchProductCategoryIds.Request()
    res = stub.fetchProductCategoryIds(req)
    if res.success:
        for category_id in res.id:
            sub_req = gb_service_pb2.FetchProductCategoryDetails.Request(categoryId=category_id)
            sub_res = stub.fetchProductCategoryDetails(sub_req)
            category_name = sub_res.name
            category_examples = sub_res.examples
            print(category_id, category_name, category_examples)
