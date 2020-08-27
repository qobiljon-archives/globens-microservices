# import the generated grpcs
from gb_grpcs import gb_service_pb2_grpc
from gb_grpcs import gb_service_pb2
# others
from concurrent import futures
from tools import db_mgr as db
from tools import utils
import grpc
import time
import json


class GlobensServiceServicer(gb_service_pb2_grpc.GlobensServiceServicer):
    # region user management module
    def authenticateUser(self, request, context):
        result = gb_service_pb2.AuthenticateUser.Response()
        result.success = False

        method = request.method
        tokens = json.loads(s=request.tokensJson)

        if method == gb_service_pb2.AuthenticateUser.AuthMethod.GOOGLE:
            print(tokens)
            user_profile = utils.load_google_profile(id_token=tokens['idToken'])
            db_user, session_key = db.create_or_update_user(
                email=user_profile['email'],
                name=user_profile['name'],
                picture=user_profile['picture'],
                tokens=request.tokensJson
            )
            result.sessionKey = session_key
            result.success = True
        elif method == gb_service_pb2.AuthenticateUser.AuthMethod.FACEBOOK:
            print(request.tokensJson)
            user_profile = utils.load_facebook_profile(access_token=tokens['accessToken'])
            db_user, session_key = db.create_or_update_user(
                email=user_profile['email'],
                name=user_profile['name'],
                picture=user_profile['picture'],
                tokens=request.tokensJson
            )
            result.sessionKey = session_key
            result.success = True
        elif method == gb_service_pb2.AuthenticateUser.AuthMethod.KAKAOTALK:
            print(tokens['accessToken'])
        elif method == gb_service_pb2.AuthenticateUser.AuthMethod.PHONE:
            print(tokens)
        elif method == gb_service_pb2.AuthenticateUser.AuthMethod.APPLE:
            print(tokens)

        return result

    def deactivateUser(self, request, context):
        # todo fill this part
        pass

    def updateUserDetails(self, request, context):
        # todo fill this part
        pass

    def fetchUserDetails(self, request, context):
        # todo fill this part
        pass

    # endregion

    # region vacancy management module
    def createVacancy(self, request, context):
        # todo fill this part
        pass

    def updateVacancyDetails(self, request, context):
        # todo fill this part
        pass

    def uncreateVacancy(self, request, context):
        # todo fill this part
        pass

    def fetchVacancies(self, request, context):
        # todo fill this part
        pass

    def fetchVacancyDetails(self, request, context):
        # todo fill this part
        pass

    # endregion

    # region vacancy application management module
    def createVacancyApplication(self, request, context):
        # todo fill this part
        pass

    def updateVacancyApplicationDetails(self, request, context):
        # todo fill this part
        pass

    def uncreateVacancyApplication(self, request, context):
        # todo fill this part
        pass

    def fetchMyVacancyApplications(self, request, context):
        # todo fill this part
        pass

    def fetchVacancyApplicationDetails(self, request, context):
        # todo fill this part
        pass

    # endregion

    # region business page management module
    def createBusinessPage(self, request, context):
        # todo fill this part
        pass

    def updateBusinessPageDetails(self, request, context):
        # todo fill this part
        pass

    def uncreateBusinessPage(self, request, context):
        # todo fill this part
        pass

    def fetchBusinessPages(self, request, context):
        # todo fill this part
        pass

    def fetchBusinessPageDetails(self, request, context):
        # todo fill this part
        pass

    # endregion

    # region product management module
    def createProduct(self, request, context):
        # todo fill this part
        pass

    def updateProductDetails(self, request, context):
        # todo fill this part
        pass

    def uncreateProduct(self, request, context):
        # todo fill this part
        pass

    def publishProduct(self, request, context):
        # todo fill this part
        pass

    def unpublishProduct(self, request, context):
        # todo fill this part
        pass

    def fetchProducts(self, request, context):
        # todo fill this part
        pass

    def fetchProductDetails(self, request, context):
        # todo fill this part
        pass

    # endregion

    # region purchase management module
    def logPurchase(self, request, context):
        # todo fill this part
        pass

    def fetchPurchases(self, request, context):
        # todo fill this part
        pass

    def fetchPurchaseDetails(self, request, context):
        # todo fill this part
        pass

    # endregion

    # region test proto (rpc)
    def testSum(self, request, context):
        res = gb_service_pb2.TestSum.Response()
        res.c = request.a + request.b
        return res
    # endregion


if __name__ == '__main__':
    print('Starting gRPC server on port 50052.')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gb_service_pb2_grpc.add_GlobensServiceServicer_to_server(servicer=GlobensServiceServicer(), server=server)
    server.add_insecure_port('0.0.0.0:50052')  # TODO: check the address!!!
    server.start()

    try:
        # since server.start() will not block, a sleep-loop is added to keep alive
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        db.end()
        print('Server has stopped.')
