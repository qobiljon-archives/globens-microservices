import grpc

# import the generated classes
from gb_grpcs import gb_service_pb2
from gb_grpcs import gb_service_pb2_grpc

# open a gRPC channel
channel = grpc.insecure_channel('165.246.42.172:50051')

# create a stub (client)
stub = gb_service_pb2_grpc.GlobensServiceStub(channel)

if __name__ == '__main__':
    req = gb_service_pb2.FetchProductDetails.Request(
        productId=7
    )
    res = stub.fetchProductDetails(req)
    content = res.content
    print(content)

    req = gb_service_pb2.FetchNextKProductIds.Request(
        k=100
    )
    res = stub.fetchNextKProductIds(req)
    if res.success:
        for product_id in res.id:
            sub_req = gb_service_pb2.FetchProductDetails.Request(
                productId=product_id
            )
            sub_res = stub.fetchProductDetails(sub_req)
            product_name = sub_res.name

            sub_req = gb_service_pb2.UpdateProductDetails.Request(
                sessionKey='2cd6db0319251b8113b3855936126de0',
                productId=product_id,
                businessPageId=sub_res.businessPageId,
                name=sub_res.name,
                type=sub_res.type,
                categoryId=sub_res.categoryId,
                pictureBlob=sub_res.pictureBlob,
                price=sub_res.price,
                currency=sub_res.currency,
                description=sub_res.description,
                content=content
            )
            sub_res = stub.updateProductDetails(sub_req)
            print(product_id, product_name, sub_res.success)
