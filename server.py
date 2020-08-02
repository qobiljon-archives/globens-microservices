import grpc
from concurrent import futures
from tools import db_mgr as db
import time

# import the generated classes
from et_grpcs import et_service_pb2
from et_grpcs import et_service_pb2_grpc

db.init()


class ETServiceServicer(et_service_pb2_grpc.ETServiceServicer):
    def loginWithGoogleId(self, request, context):
        res = et_service_pb2.LoginResponseMessage()
        try:
            user = db.get_existing_user_by_id_token(id_token=request.idToken)
            if user is None:
                user = db.register_user(id_token=request.idToken)
                if user is None:
                    res.doneSuccessfully = False
                    print('loginWithGoogleId(register); success = False; idToken = ', request.idToken)
                else:
                    res.doneSuccessfully = True
                    res.userId = user[0]
                    print('loginWithGoogleId(register); success = True; email =', user[3])
            else:
                res.doneSuccessfully = True
                res.userId = user[0]
                print('loginWithGoogleId(login); success = True; email =', user[3])
        except ValueError as e:
            res.doneSuccessfully = False
            print('loginWithGoogleId(error)', e)
        return res

    def bindUserToCampaign(self, request, context):
        res = et_service_pb2.BindUserToCampaignResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        campaign = db.get_campaign_by_id(request.campaignId)
        res.doneSuccessfully = user is not None and user[0] == request.userId and campaign is not None
        if res.doneSuccessfully:
            if db.campaign_has_started(campaign_id=request.campaignId):
                res.isFirstTimeBinding = db.bind_participant_to_campaign(user_id=request.userId, campaign_id=request.campaignId)
            else:
                res.doneSuccessfully = False
            res.campaignStartTimestamp = db.get_campaign_start_timestamp(campaign_id=request.campaignId)
        print('bindUserToCampaign(newBinding={0}); success ={1}'.format(res.isFirstTimeBinding, res.doneSuccessfully))
        return res

    def dashboardLoginWithEmail(self, request, context):
        res = et_service_pb2.LoginResponseMessage()
        if request.dashboardKey == 'ETd@$#b0@rd':
            try:
                user = db.get_existing_user_by_email(email=request.email)
                if user is None:
                    user = db.create_user(id_token=None, name=request.name, email=request.email)
                    if user is None:
                        res.doneSuccessfully = False
                        print('dashboardLoginWithEmail(register); success = False, email = ', request.email)
                    else:
                        res.doneSuccessfully = True
                        res.userId = user[0]
                        print('dashboardLoginWithEmail(register); success = True, email = ', request.email)
                else:
                    res.doneSuccessfully = True
                    res.userId = user[0]
                    print('dashboardLoginWithEmail(login); success = True, email = ', request.email)
            except ValueError as e:
                res.doneSuccessfully = False
                print('dashboardLoginWithEmail(); error = ', e)
        else:
            res.doneSuccessfully = False
            print('dashboardLoginWithEmail(); success = False, dashboardKey = ', request.dashboardKey)
        return res

    def registerCampaign(self, request, context):
        res = et_service_pb2.RegisterCampaignResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId
        if res.doneSuccessfully:
            db.create_or_update_campaign(
                campaign_id=request.campaignId,
                creator_id=request.userId,
                name=request.name,
                notes=request.notes,
                configurations=request.configJson,
                start_timestamp=request.startTimestamp,
                end_timestamp=request.endTimestamp
            )
        print('registerCampaign(); success =', res.doneSuccessfully)
        return res

    def deleteCampaign(self, request, context):
        res = et_service_pb2.DefaultResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        campaign = db.get_campaign_by_id(campaign_id=request.campaignId)
        res.doneSuccessfully = user is not None and user[0] == request.userId and user[1] is None and campaign is not None and campaign[1] == user[0]
        if res.doneSuccessfully:
            # creator made the delete request, so delete it
            db.delete_campaign(campaign_id=campaign[0])
        print('deleteCampaign(); success =', res.doneSuccessfully)
        return res

    def retrieveCampaigns(self, request, context):
        res = et_service_pb2.RetrieveCampaignsResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId
        if res.doneSuccessfully:
            campaigns = db.get_campaigns(creator_id=request.userId) if request.myCampaignsOnly else db.get_campaigns()
            for row in campaigns:
                res.campaignId.extend([row[0]])
                res.creatorEmail.extend([db.get_email_by_user_id(user_id=row[1])])
                res.name.extend([row[2]])
                res.notes.extend([row[3]])
                res.configJson.extend([row[4]])
                res.startTimestamp.extend([row[5]])
                res.endTimestamp.extend([row[6]])
                res.participantCount.extend([db.get_campaigns_participant_count(campaign_id=row[0])])
        print('retrieveCampaigns(); success =', res.doneSuccessfully)
        return res

    def retrieveCampaign(self, request, context):
        res = et_service_pb2.RetrieveCampaignResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        campaign = db.get_campaign_by_id(campaign_id=request.campaignId)
        res.doneSuccessfully = user is not None and user[0] == request.userId and campaign is not None
        res.doneSuccessfully &= user[1] is None or db.is_participant_bound_to_campaign(user_id=user[0], campaign_id=campaign[0])
        if res.doneSuccessfully:
            res.name = campaign[2]
            res.notes = campaign[3]
            res.creatorEmail = db.get_email_by_user_id(user_id=campaign[1])
            res.startTimestamp = campaign[5]
            res.endTimestamp = campaign[6]
            res.configJson = campaign[4]
            res.participantCount = db.get_campaigns_participant_count(campaign_id=campaign[0])
        print('retrieveCampaign(); success =', res.doneSuccessfully)
        return res

    def submitDataRecord(self, request, context):
        res = et_service_pb2.DefaultResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId and db.store_data_record(
            user_id=user[0],
            timestamp_ms=request.timestamp,
            data_source_id=request.dataSource,
            values=request.values
        )
        if res.doneSuccessfully:
            campaign_id = db.get_participants_current_campaign_id(user_id=user[0])
            db.update_sync_timestamp(user_id=user[0], campaign_id=campaign_id, data_source_id=request.dataSource, sync_timestamp=request.timestamp)
        # print('submitData(); success =', res.doneSuccessfully)
        return res

    def submitDataRecords(self, request, context):
        res = et_service_pb2.DefaultResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId
        if res.doneSuccessfully:
            latest_sync_timestamp = 0
            valid = False
            for timestamp, dataSource, values in zip(request.timestamp, request.dataSource, request.values):
                _valid = db.store_data_record(
                    user_id=user[0],
                    timestamp_ms=timestamp,
                    data_source_id=dataSource,
                    values=values
                )
                if _valid:
                    campaign_id = db.get_participants_current_campaign_id(user_id=user[0])
                    db.update_sync_timestamp(user_id=user[0], campaign_id=campaign_id, data_source_id=dataSource, sync_timestamp=latest_sync_timestamp)
                valid |= _valid
                latest_sync_timestamp = max(latest_sync_timestamp, timestamp)
            res.doneSuccessfully = valid
        # print('submitData(); success =', res.doneSuccessfully)
        return res

    def submitHeartbeat(self, request, context):
        res = et_service_pb2.DefaultResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId
        if res.doneSuccessfully:
            # campaign_id = db.get_participants_current_campaign_id(user_id=user[0])
            # campaign = None if campaign_id is None else db.get_campaign_by_id(campaign_id=campaign_id)
            # res.doneSuccessfully = campaign_id is not None and campaign is not None and campaign[6] >= utils.get_timestamp_ms()
            # if res.doneSuccessfully:
            db.update_user_heartbeat_timestamp(user_id=request.userId)
        # print('submitHeartbeat(); success =', res.doneSuccessfully)
        return res

    def submitDirectMessage(self, request, context):
        res = et_service_pb2.DefaultResponseMessage()
        src_user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = src_user is not None and src_user[0] == request.userId
        trg_user = db.get_existing_user_by_email(request.targetEmail)
        res.doneSuccessfully = res.doneSuccessfully and trg_user is not None
        if res.doneSuccessfully:
            db.store_direct_message(
                src_user_id=src_user[0],
                trg_user_id=trg_user[0],
                subject=request.subject,
                content=request.content
            )
        # print('submitDirectMessage(); success =', res.doneSuccessfully)
        return res

    def retrieveParticipants(self, request, context):
        res = et_service_pb2.RetrieveParticipantsResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId
        campaign = db.get_campaign_by_id(campaign_id=request.campaignId)
        res.doneSuccessfully = campaign is not None and campaign[1] == user[0]
        if res.doneSuccessfully:
            for row in db.get_participants_of_campaign(campaign_id=campaign[0]):
                res.userId.extend([row[0]])
                res.name.extend([row[2]])
                res.email.extend([row[3]])
        # print('retrieveParticipants(); success =', res.doneSuccessfully)
        return res

    def retrieveParticipantStatistics(self, request, context):
        res = et_service_pb2.RetrieveParticipantStatisticsResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        trg_user = db.get_existing_user_by_email(request.targetEmail)
        trg_campaign = db.get_campaign_by_id(campaign_id=request.targetCampaignId)
        res.doneSuccessfully = user is not None and user[0] == request.userId and trg_user is not None and trg_campaign is not None
        if res.doneSuccessfully:
            active_campaign_id = db.get_participants_current_campaign_id(user_id=trg_user[0])
            res.activeCampaignId = -1 if active_campaign_id is None else active_campaign_id
            res.campaignJoinTimestamp = db.get_participant_join_timestamp(user_id=trg_user[0], campaign_id=trg_campaign[0])
            res.lastSyncTimestamp = db.get_participant_last_sync_timestamp(user_id=trg_user[0], campaign_id=trg_campaign[0])
            res.lastHeartbeatTimestamp = trg_user[5]
            res.amountOfSubmittedDataSamples = db.get_participants_amount_of_data(user_id=trg_user[0], campaign_id=trg_campaign[0])
            for data_source_id, amount_of_data, last_sync_time in db.get_participants_stats_per_data_source(user_id=trg_user[0], campaign=trg_campaign):
                res.dataSourceId.extend([data_source_id])
                res.perDataSourceAmountOfData.extend([amount_of_data])
                res.perDataSourceLastSyncTimestamp.extend([last_sync_time])
        # print('retrieveParticipantStatistics(); success =', res.doneSuccessfully)
        return res

    def retrieve100DataRecords(self, request, context):
        res = et_service_pb2.Retrieve100DataRecordsResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        trg_user = db.get_existing_user_by_email(request.targetEmail)
        trg_campaign = db.get_campaign_by_id(campaign_id=request.targetCampaignId)
        res.doneSuccessfully = user is not None and user[0] == request.userId and trg_user is not None and trg_campaign is not None
        if res.doneSuccessfully:
            rows, more_data_available = db.get_next_100_filtered_data(user_id=trg_user[0], campaign=trg_campaign, from_timestamp=request.fromTimestamp, data_source_id=request.targetDataSourceId)
            res.moreDataAvailable = more_data_available
            for row in rows:
                res.timestamp.extend([row[1]])
                res.dataSource.extend([row[2]])
                res.value.extend([row[3]])
        # print('retrieve100DataRecords(); success =', res.doneSuccessfully)
        return res

    def retrieveFilteredDataRecords(self, request, context):
        res = et_service_pb2.RetrieveFilteredDataRecordsResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        trg_user = db.get_existing_user_by_email(request.targetEmail)
        trg_campaign = db.get_campaign_by_id(campaign_id=request.targetCampaignId)
        res.doneSuccessfully = user is not None and user[0] == request.userId and trg_user is not None and trg_campaign is not None
        if res.doneSuccessfully:
            rows = db.get_filtered_data(user_id=trg_user[0], campaign=trg_campaign, data_source_id=request.targetDataSourceId, from_timestamp=request.fromTimestamp, till_timestamp=request.tillTimestamp)
            for row in rows:
                res.timestamp.extend([row[1]])
                res.dataSource.extend([row[2]])
                res.value.extend([row[3]])
        # print('retrieveFilteredDataRecords(); success =', res.doneSuccessfully)
        return res

    def retrieveUnreadDirectMessages(self, request, context):
        res = et_service_pb2.RetrieveUnreadDirectMessagesResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId
        if res.doneSuccessfully:
            for row in db.get_unread_direct_messages(user_id=user[0]):
                res.sourceEmail.extend([db.get_email_by_user_id(user_id=row[0])])
                res.timestamp.extend([row[2]])
                res.subject.extend([row[3]])
                res.content.extend([row[4]])
        print('retrieveUnreadDirectMessages(); success =', res.doneSuccessfully)
        return res

    def retrieveUnreadNotifications(self, request, context):
        res = et_service_pb2.RetrieveUnreadNotificationsResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId
        if res.doneSuccessfully:
            for row in db.get_unread_notifications(user_id=user[0]):
                res.timestamp.extend([row[1]])
                res.subject.extend([row[2]])
                res.content.extend([row[3]])
        print('retrieveUnreadDirectMessages(); success =', res.doneSuccessfully)
        return res

    def bindDataSource(self, request, context):
        res = et_service_pb2.BindDataSourceResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId
        if res.doneSuccessfully:
            data_source = db.get_data_source_by_name(name=request.name)
            if data_source is None:
                db.create_data_source(creator_id=user[0], name=request.name, icon_name=request.iconName)
                data_source = db.get_data_source_by_name(name=request.name)
                print('bindDataSource(create); success =', res.doneSuccessfully)
            else:
                print('bindDataSource(); success =', res.doneSuccessfully)
            res.doneSuccessfully = True
            res.dataSourceId = data_source[0]
            res.iconName = data_source[3]
        return res

    def retrieveAllDataSources(self, request, context):
        res = et_service_pb2.RetrieveAllDataSourcesResponseMessage()
        user = db.get_existing_user_by_email(request.email)
        res.doneSuccessfully = user is not None and user[0] == request.userId
        if res.doneSuccessfully:
            for row in db.get_all_data_sources():
                res.dataSourceId.extend([row[0]])
                res.creatorEmail.extend([db.get_email_by_user_id(user_id=row[1])])
                res.name.extend([row[2]])
                res.iconName.extend([row[3]])
        print('retrieveAllDataSources(); success =', res.doneSuccessfully)
        return res


# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# use the generated function `add_ETServiceServicer_to_server` to add the defined class to the server
et_service_pb2_grpc.add_ETServiceServicer_to_server(ETServiceServicer(), server)

# listen on port 50051 [ server.add_insecure_port('[::]:50051') ]
print('Starting gRPC server on port 50051.')
server.add_insecure_port('165.246.21.202:50051')  # TODO: check the address!!!
server.start()

# since server.start() will not block, a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
    db.end()
    print('Server has stopped.')
