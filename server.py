# import the generated gRPCs
from gb_grpcs import gb_service_pb2_grpc
from gb_grpcs import gb_service_pb2
# others
from concurrent import futures
from tools import db_mgr as db
from datetime import datetime
from tools import utils
import grpc
import time
import json


class GlobensServiceServicer(gb_service_pb2_grpc.GlobensServiceServicer):
    # region user management module
    def authenticateUser(self, request, context):
        print(f' authenticateUser')
        response = gb_service_pb2.AuthenticateUser.Response()
        response.success = False

        tokens = json.loads(s=request.tokensJson)
        user_profile = utils.load_google_profile(id_token=tokens['idToken'])
        gb_user = db.get_user(email=user_profile['email'])

        if gb_user is None:
            gb_user, session_key = db.create_user(
                email=user_profile['email'],
                name=user_profile['name'],
                picture=user_profile['picture'],
                tokens=request.tokensJson
            )
        else:
            session_key = gb_user['sessionKey']

        response.userId = gb_user['id']
        response.sessionKey = session_key
        response.success = True

        print(f' authenticateUser, success={response.success}')
        return response

    def deactivateUser(self, request, context):
        print(f' deactivateUser')
        # todo deactivate user
        print(f' deactivateUser')

    def updateUserDetails(self, request, context):
        print(f' updateUserDetails')
        response = gb_service_pb2.UpdateUserDetails.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)

        if gb_user is not None:
            db.update_user(gb_user=gb_user, country_code=request.countryCode)
            response.success = True

        print(f' updateUserDetails, success={response.success}')
        return response

    def fetchUserDetails(self, request, context):
        # print(f' fetchUserDetails')
        response = gb_service_pb2.FetchUserDetails.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_target_user = db.get_user(user_id=request.userId)

        if None not in [gb_user, gb_target_user]:
            response.id = gb_target_user['id']
            response.email = gb_target_user['email']
            response.name = gb_target_user['name']
            response.picture = gb_target_user['picture']
            response.pictureBlob = bytes(gb_target_user['pictureBlob'])
            response.success = True

        # print(f' fetchUserDetails, success={response.success}')
        return response

    # endregion

    # region job/vacancy management module
    def createVacantJob(self, request, context):
        print(f' createVacantJob')
        response = gb_service_pb2.CreateVacantJob.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_business_page = db.get_business_page(business_page_id=request.businessPageId)

        if None not in [gb_user, gb_business_page]:
            db.create_vacant_job(gb_user=gb_user, gb_business_page=gb_business_page, title=request.title)
            response.success = True

        print(f' createVacancy, success={response.success}')
        return response

    def updateJobDetails(self, request, context):
        print(f' updateJobDetails')
        # todo update job details
        print(f' updateJobDetails')

    def uncreateJob(self, request, context):
        print(f' uncreateJob')
        # todo uncreate job
        print(f' uncreateJob')

    def fetchBusinessPageJobIds(self, request, context):
        # print(f' fetchBusinessPageJobIds')
        response = gb_service_pb2.FetchBusinessPageJobIds.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_business_page = db.get_business_page(business_page_id=request.businessPageId)

        if None not in [gb_user, gb_business_page]:
            response.id.extend(db.get_business_page_job_ids(gb_business_page=gb_business_page))
            response.success = True

        # print(f' fetchBusinessPageJobIds, success={response.success}')
        return response

    def fetchNextKVacantJobIds(self, request, context):
        # print(f' fetchNextKVacantJobIds')
        response = gb_service_pb2.FetchNextKVacantJobIds.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        k = request.k
        filter_details = request.filterDetails
        previous_vacant_job_id = request.previousVacantJobId

        if None not in [gb_user, k, filter_details] and k <= 250:
            for gb_vacant_job in db.get_next_k_vacant_jobs(previous_vacant_job_id=previous_vacant_job_id, k=k, filter_details=filter_details):
                response.id.extend([gb_vacant_job['id']])
            response.success = True

        # print(f' fetchNextKVacancyJobIds, success={response.success}')
        return response

    def fetchJobDetails(self, request, context):
        # print(f' fetchJobDetails')
        response = gb_service_pb2.FetchJobDetails.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_job = db.get_job(job_id=request.jobId)

        if None not in [gb_user, gb_job]:
            response.id = gb_job['id']
            response.businessPageId = gb_job['business_page_id']
            response.role = gb_job['role']
            response.title = gb_job['title']
            response.hiredUserId = gb_job['user_id'] if gb_job['user_id'] is not None else -1
            response.success = True

        # print(f' fetchJobDetails, success={response.success}')
        return response

    # endregion

    # region vacancy application management module
    def createJobApplication(self, request, context):
        print(f' createJobApplication')
        response = gb_service_pb2.CreateJobApplication.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_job = db.get_job(job_id=request.jobId)

        if None not in [gb_user, gb_job] and gb_job['user_id'] is None and not db.job_application_exists(gb_user=gb_user, gb_job=gb_job):
            db.create_job_application(gb_user=gb_user, gb_job=gb_job, message=request.message, content=request.content)
            response.success = True

        print(f' createJobApplication, success={response.success}')
        return response

    def updateJobApplicationDetails(self, request, context):
        print(f' updateJobApplicationDetails')
        # todo update vacancy application
        print(f' updateJobApplicationDetails')

    def uncreateJobApplication(self, request, context):
        print(f' uncreateJobApplication')
        # todo uncreate vacancy application
        print(f' uncreateJobApplication')

    def fetchJobApplicationIds(self, request, context):
        print(f' fetchJobApplicationIds')
        response = gb_service_pb2.FetchJobApplicationIds.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_job = db.get_job(job_id=request.jobId)

        if None not in [gb_user, gb_job]:
            response.id.extend(db.get_job_application_ids(gb_job=gb_job))
            response.success = True

        print(f' fetchJobApplicationIds, success={response.success}')
        return response

    def fetchJobApplicationDetails(self, request, context):
        print(f' fetchJobApplicationDetails')
        response = gb_service_pb2.FetchJobApplicationDetails.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_job_application = db.get_job_application(job_application_id=request.jobApplicationId)

        if None not in [gb_user, gb_job_application]:
            response.id = gb_job_application['id']
            response.message = gb_job_application['message']
            response.content = bytes(gb_job_application['content'])
            response.applicantId = gb_job_application['user_id']
            response.success = True

        print(f' fetchJobApplicationDetails, success={response.success}')
        return response

    def approveJobApplication(self, request, context):
        print(f' approveJobApplication')
        response = gb_service_pb2.ApproveJobApplication.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_job_application = db.get_job_application(job_application_id=request.jobApplicationId)

        if None not in [gb_user, gb_job_application]:
            db.approve_job_application(gb_job_application=gb_job_application)
            response.success = True

        print(f' approveJobApplication, success={response.success}')
        return response

    def declineJobApplication(self, request, context):
        print(f' declineJobApplication')
        response = gb_service_pb2.DeclineJobApplication.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_job_application = db.get_job_application(job_application_id=request.jobApplicationId)

        if None not in [gb_user, gb_job_application]:
            db.decline_job_application(gb_job_application=gb_job_application)
            response.success = True

        print(f' declineJobApplication, success={response.success}')
        return response

    # endregion

    # region business page management module
    def createBusinessPage(self, request, context):
        print(f' createBusinessPage')
        response = gb_service_pb2.CreateBusinessPage.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)

        if gb_user is not None:
            db.create_business_page(gb_user=gb_user, title=request.title, picture_blob=request.pictureBlob, country_code=request.countryCode)
            response.success = True

        print(f' createBusinessPage, success={response.success}')
        return response

    def updateBusinessPageDetails(self, request, context):
        print(f' updateBusinessPageDetails')
        response = gb_service_pb2.UpdateBusinessPageDetails.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_business_page = db.get_business_page(business_page_id=request.businessPageId)

        if None not in [gb_user, gb_business_page] and db.get_user_role_in_business_page(gb_user=gb_user, gb_business_page=gb_business_page) in ['business owner', 'individual entrepreneur']:
            db.update_business_page_details(gb_business_page=gb_business_page, title=request.title, picture_blob=request.pictureBlob, country_code=request.countryCode)
            response.success = True

        print(f' updateBusinessPageDetails, success={response.success}')
        return response

    def uncreateBusinessPage(self, request, context):
        print(f' uncreateBusinessPage')
        # todo uncreate business page
        print(f' uncreateBusinessPage')

    def fetchMyBusinessPageIds(self, request, context):
        print(f' fetchMyBusinessPageIds')
        response = gb_service_pb2.FetchMyBusinessPageIds.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)

        if gb_user is not None:
            response.id.extend(db.get_business_page_ids(gb_user=gb_user))
            response.success = True

        print(f' fetchMyBusinessPageIds, success={response.success}')
        return response

    def fetchBusinessPageDetails(self, request, context):
        print(f' fetchBusinessPageDetails')
        response = gb_service_pb2.FetchBusinessPageDetails.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_business_page = db.get_business_page(business_page_id=request.businessPageId)

        if None not in [gb_business_page]:
            response.id = gb_business_page['id']
            response.title = gb_business_page['title']
            response.type = gb_business_page['type']
            response.pictureBlob = bytes(gb_business_page['pictureBlob'])
            response.countryCode = gb_business_page['countryCode']
            response.role = db.get_user_role_in_business_page(gb_user=gb_user, gb_business_page=gb_business_page) if gb_user is not None else "consumer"
            response.success = True

        print(f' fetchBusinessPageDetails, success={response.success}')
        return response

    # endregion

    # region product management module
    def createProduct(self, request, context):
        print(f' createProduct')
        response = gb_service_pb2.CreateProduct.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_business_page = db.get_business_page(business_page_id=request.businessPageId)
        gb_category = db.get_product_category(category_id=request.categoryId)

        if None not in [gb_user, gb_business_page, gb_category]:
            response.productId = db.create_product(gb_user=gb_user, gb_business_page=gb_business_page, gb_category=gb_category, name=request.name, product_type=utils.get_product_type_str(request.type), picture_blob=request.pictureBlob, price=request.price, currency=utils.get_currency_str(currency=request.currency), description=request.description, contents=request.contents)
            response.success = True

        print(f' createProduct, success={response.success}')
        return response

    def updateProductDetails(self, request, context):
        print(f' updateProductDetails')
        response = gb_service_pb2.UpdateProductDetails.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_product = db.get_product(product_id=request.productId)
        gb_business_page = db.get_business_page(business_page_id=request.businessPageId)
        gb_category = db.get_product_category(category_id=request.categoryId)

        if None not in [gb_user, gb_product, gb_category, gb_business_page]:
            db.update_product(gb_product=gb_product, gb_business_page=gb_business_page, gb_category=gb_category, name=request.name, product_type=utils.get_product_type_str(request.type), picture_blob=request.pictureBlob, price=request.price, currency=utils.get_currency_str(currency=request.currency), description=request.description, contents=request.contents)
            response.success = True

        print(f' updateProductDetails, success={response.success}')
        return response

    def uncreateProduct(self, request, context):
        print(f' uncreateProduct')
        # todo uncreate product
        print(f' uncreateProduct')

    def publishProduct(self, request, context):
        print(f' publishProduct')
        response = gb_service_pb2.PublishProduct.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_product = db.get_product(product_id=request.productId)
        gb_product_business_page = None
        if gb_product:
            gb_product_business_page = db.get_business_page(business_page_id=gb_product['business_page_id'])

        if None not in [gb_user, gb_product, gb_product_business_page]:
            role = db.get_user_role_in_business_page(gb_user=gb_user, gb_business_page=gb_product_business_page)
            if role == 'individual entrepreneur' or role == 'business owner':
                db.publish_product(gb_product=gb_product)
                response.success = True

        print(f' publishProduct, success={response.success}')
        return response

    def unpublishProduct(self, request, context):
        print(f' unpublishProduct')
        response = gb_service_pb2.UnpublishProduct.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_product = db.get_product(product_id=request.productId)
        gb_product_business_page = None
        if gb_product:
            gb_product_business_page = db.get_business_page(business_page_id=gb_product['business_page_id'])

        if None not in [gb_user, gb_product, gb_product_business_page] and db.get_user_role_in_business_page(gb_user=gb_user, gb_business_page=gb_product_business_page) == 'business owner':
            db.unpublish_product(gb_product=gb_product)
            response.success = True

        print(f' unpublishProduct, success={response.success}')
        return response

    def createNewContent(self, request, context):
        print(f' createNewContent')
        response = gb_service_pb2.CreateNewContent.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)

        if gb_user is not None:
            response.contentId = db.create_content(title=request.title, file_id=request.fileId, url=request.url)
            response.success = True

        print(f' createNewContent, success={response.success}')
        return response

    def updateContent(self, request, context):
        print(f' updateContent')
        response = gb_service_pb2.UpdateContent.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_content = db.get_content(content_id=request.contentId)

        if None not in [gb_user, gb_content]:
            db.update_content(gb_content=gb_content, title=request.title, file_id=request.fileId, url=request.url)
            response.success = True

        print(f' updateContent, success={response.success}')
        return response

    def fetchContentDetails(self, request, context):
        # print(f' fetchContentDetails')
        response = gb_service_pb2.FetchContentDetails.Response()
        response.success = False

        gb_content = db.get_content(content_id=request.contentId)
        if None not in [gb_content]:
            response.id = gb_content['id']
            response.title = gb_content['title']
            response.fileId = gb_content['file_id']
            response.url = gb_content['url']
            response.success = True

        # print(f' fetchContentDetails, success={response.success}')
        return response

    def deleteContent(self, request, context):
        print(f' deleteContent')
        response = gb_service_pb2.DeleteContent.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_content = db.get_content(content_id=request.contentId)

        if None not in [gb_user, gb_content]:
            db.delete_content(gb_content=gb_content)
            response.success = True

        print(f' deleteContent, success={response.success}')
        return response

    def fetchNextKProductIds(self, request, context):
        # print(f' fetchNextKProductIds')
        response = gb_service_pb2.FetchNextKProductIds.Response()
        response.success = False

        k = request.k
        filter_details = request.filterDetails
        previous_product_id = request.previousProductId

        if None not in [k, filter_details] and k <= 250:
            for gb_product in db.get_next_k_products(previous_product_id=previous_product_id, k=k, filter_details=filter_details):
                response.id.extend([gb_product['id']])
            response.success = True

        # print(f' fetchNextKProductIds, success={response.success}')
        return response

    def fetchProductDetails(self, request, context):
        # print(f' fetchProductDetails')
        response = gb_service_pb2.FetchProductDetails.Response()
        response.success = False

        gb_product = db.get_product(product_id=request.productId)
        if None not in [gb_product]:
            response.id = gb_product['id']
            response.name = gb_product['name']
            response.type = utils.get_product_type_enum(gb_product['productType'])
            response.categoryId = gb_product['category_id']
            response.published = gb_product['published']
            response.pictureBlob = bytes(gb_product['pictureBlob'])
            response.businessPageId = gb_product['business_page_id']
            response.price = gb_product['price']
            response.stars = gb_product['stars']
            response.reviewsCount = gb_product['reviewsCount']
            response.currency = utils.get_currency_enum(currency_str=gb_product['currency'])
            response.description = gb_product['description']
            response.contents = gb_product['contents']
            response.success = True

        # print(f' fetchProductDetails, success={response.success}')
        return response

    def fetchProductCategoryIds(self, request, context):
        # print(f' fetchProductCategoryIds')
        response = gb_service_pb2.FetchProductCategoryIds.Response()
        response.success = True

        for gb_category in db.get_product_categories():
            response.id.extend([gb_category['id']])

        # print(f' fetchProductCategoryIds, success={response.success}')
        return response

    def fetchProductCategoryDetails(self, request, context):
        # print(f' fetchProductCategoryDetails')
        response = gb_service_pb2.FetchProductCategoryDetails.Response()
        response.success = False

        db_category = db.get_product_category(category_id=request.categoryId)

        if None not in [db_category]:
            response.id = db_category['id']
            response.nameJsonStr = db_category['name']
            response.pictureBlob = bytes(db_category['pictureBlob'])
            response.examplesJsonStr = db_category['examples']
            response.success = True

        # print(f' fetchProductCategoryDetails, success={response.success}')
        return response

    # endregion

    # region purchase management module
    def logPurchase(self, request, context):
        print(f' logPurchase')
        # todo log purchase
        print(f' logPurchase')

    def fetchPurchases(self, request, context):
        print(f' fetchPurchases')
        # todo fetch purchases
        print(f' fetchPurchases')

    def fetchPurchaseDetails(self, request, context):
        print(f' fetchPurchaseDetails')
        # todo fetch purchase details
        print(f' fetchPurchaseDetails')

    # endregion

    # region review management module
    def submitProductReview(self, request, context):
        print(f' submitProductReview')
        response = gb_service_pb2.SubmitProductReview.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_product = db.get_product(product_id=request.productId)

        if None not in [gb_user, gb_product]:
            db.create_or_update_product_review(gb_user=gb_user, gb_product=gb_product, stars=request.stars, text=request.text, timestamp=datetime.fromtimestamp(request.timestamp / 1000))
            response.success = True

        print(f' submitProductReview, success={response.success}')
        return response

    def retrieveProductReviews(self, request, context):
        print(f' retrieveProductReviews')
        response = gb_service_pb2.RetrieveProductReviews.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_product = db.get_product(product_id=request.productId)

        if None not in [gb_user, gb_product]:
            for gb_product_review in db.get_product_reviews(gb_product=gb_product):
                response.id.extend([gb_product_review['id']])
                response.isMyReview.extend([gb_product_review['user_id'] == gb_user['id']])
                response.stars.extend([gb_product_review['stars']])
                response.text.extend([gb_product_review['text']])
                response.timestamp.extend([int(gb_product_review['timestamp'].timestamp() * 1000)])
            response.success = True

        print(f' retrieveProductReviews, success={response.success}')
        return response

    def deleteProductReview(self, request, context):
        print(f' deleteProductReview')
        response = gb_service_pb2.DeleteProductReview.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_product_review = db.get_product_review(product_review_id=request.reviewId)

        if None not in [gb_user, gb_product_review] and gb_product_review['user_id'] == gb_user['id']:
            db.delete_product_review(gb_product_review=gb_product_review)
            response.success = True

        print(f' deleteProductReview, success={response.success}')
        return response

    def submitEmployeeReview(self, request, context):
        print(f' submitEmployeeReview')
        response = gb_service_pb2.SubmitEmployeeReview.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_business_page = db.get_business_page(business_page_id=request.businessPageId)
        gb_employee_user = db.get_user(user_id=request.employeeUserId)

        if None not in [gb_user, gb_business_page, gb_employee_user]:
            db.create_or_update_employee_review(gb_user=gb_user, gb_business_page=gb_business_page, gb_employee_user=gb_employee_user, text=request.text, timestamp=datetime.fromtimestamp(request.timestamp / 1000))
            response.success = True

        print(f' submitEmployeeReview, success={response.success}')
        return response

    def retrieveEmployeeReviews(self, request, context):
        print(f' retrieveEmployeeReviews')
        response = gb_service_pb2.RetrieveEmployeeReviews.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_business_page = db.get_business_page(business_page_id=request.businessPageId)
        gb_employee_user = db.get_user(user_id=request.employeeUserId)

        if None not in [gb_user, gb_business_page, gb_employee_user]:
            for gb_employee_review in db.get_employee_reviews(gb_business_page=gb_business_page, gb_employee_user=gb_employee_user):
                response.id.extend(gb_employee_review['id'])
                response.isMyReview.extend(gb_employee_review['user_id'] == gb_user['id'])
                response.text.extend(gb_employee_review['text'])
                response.timestamp.extend(int(gb_employee_review['timestamp'].timestamp() * 1000))
            response.success = True

        print(f' retrieveEmployeeReviews, success={response.success}')
        return response

    def deleteEmployeeReview(self, request, context):
        print(f' deleteEmployeeReview')
        response = gb_service_pb2.DeleteEmployeeReview.Response()
        response.success = False

        gb_user = db.get_user(session_key=request.sessionKey)
        gb_employee_review = db.get_employee_review(employee_review_id=request.reviewId)

        if None not in [gb_user, gb_employee_review] and gb_employee_review['user_id'] == gb_user['id']:
            db.delete_employee_review(gb_employee_review=gb_employee_review)
            response.success = True

        print(f' deleteEmployeeReview, success={response.success}')
        return response
    # endregion


if __name__ == '__main__':
    print('Starting gRPC server on port 50051.')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=999))
    gb_service_pb2_grpc.add_GlobensServiceServicer_to_server(servicer=GlobensServiceServicer(), server=server)
    server.add_insecure_port('0.0.0.0:50051')  # TODO: check the address!!!
    server.start()

    try:
        # since server.start() will not block, a sleep-loop is added to keep alive
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        db.end()
        print('Server has stopped.')
