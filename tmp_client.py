import grpc

# import the generated classes
from et_grpcs import et_service_pb2
from et_grpcs import et_service_pb2_grpc

# open a gRPC channel
channel = grpc.insecure_channel('165.246.21.202:50051')

# create a stub (client)
stub = et_service_pb2_grpc.ETServiceStub(channel)


def create_campaign():
    # make the call
    request = et_service_pb2.RegisterCampaignRequestMessage(
        userId=1,
        email='test@test.com',
        name='Test',
        notes='Test',
        configJson='{}',
        startTimestamp=1587397248000,
        endTimestamp=1587707248000
    )
    response = stub.registerCampaign(request)
    print(response)


def submit_records():
    # make the call
    req = et_service_pb2.SubmitDataRecordsRequestMessage(
        userId=1,
        email='nslabinha@gmail.com'
    )
    req.timestamp.extend([1587754742000])
    req.dataSource.extend([33])
    req.accuracy.extend([0.0])
    req.values.extend(['STATIONARY'])
    response = stub.submitDataRecords(req)
    print(response)


if __name__ == '__main__':
    # create_campaign()
    submit_records()
    channel.close()
