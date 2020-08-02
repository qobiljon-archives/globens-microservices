import psycopg2
import json
from tools import utils

# import google auth libraries
from google.oauth2 import id_token as oauth_id_token
from google.auth.transport import requests as oauth_requests

conn = None


def init():
    global conn
    conn = psycopg2.connect(
        host='165.246.42.172',
        database='globens_db',
        user='postgres',
        password='postgres'
    )
    print('database initialized', conn)


def end():
    global conn
    conn.close()


def get_existing_user_by_email(email):
    cur = conn.cursor()
    cur.execute("select * from et_users where email=%s;", (email,))
    row = cur.fetchone()
    cur.close()
    return row


def get_existing_user_by_id_token(id_token):
    google_id_details = oauth_id_token.verify_oauth2_token(id_token=id_token, request=oauth_requests.Request())
    if google_id_details['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        print('google auth failure, wrong issuer')
        return None
    try:
        return get_existing_user_by_email(email=google_id_details['email'])
    except (Exception, psycopg2.DatabaseError) as e:
        print('db_mgr.get_user', e)
        return None


def get_email_by_user_id(user_id):
    cur = conn.cursor()
    cur.execute("select email from et_users where id=%s;", (user_id,))
    row = cur.fetchone()
    cur.close()
    return row[0]


def register_user(id_token):
    google_id_details = oauth_id_token.verify_oauth2_token(id_token=id_token, request=oauth_requests.Request())
    if google_id_details['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        print('google auth failure, wrong issuer')
        return None
    try:
        return create_user(id_token=id_token, name=google_id_details['name'], email=google_id_details['email'])
    except (Exception, psycopg2.DatabaseError) as e:
        print('db_mgr.register_user', e)
        return None


def create_user(id_token, name, email):
    cur = conn.cursor()
    timestamp_now = utils.get_timestamp_ms()
    cur.execute("insert into et_users(id_token, name, email, last_heartbeat_timestamp) values (%s,%s,%s,%s);", (
        id_token,
        name,
        email,
        timestamp_now
    ))
    cur.close()
    conn.commit()
    return get_existing_user_by_email(email=email)


def get_participants_of_campaign(campaign_id=None):
    cur = conn.cursor()
    if campaign_id is None:
        cur.execute("select * from et_users where id_token is not null;")
    else:
        cur.execute("select * from et_users where id in (select user_id from et_campaign_to_user_maps where campaign_id=%s);", (campaign_id,))
    rows = cur.fetchall()
    cur.close()
    return rows


def get_participants_current_campaign_id(user_id):
    cur = conn.cursor()
    cur.execute('select campaign_id from et_users where id=%s;', (user_id,))
    campaign_id = cur.fetchone()[0]
    cur.close()
    return campaign_id


def get_participant_join_timestamp(user_id, campaign_id):
    cur = conn.cursor()
    cur.execute('select join_timestamp from et_campaign_to_user_maps where user_id=%s and campaign_id=%s;', (
        user_id,
        campaign_id
    ))
    join_timestamp = cur.fetchone()[0]
    cur.close()
    return join_timestamp


def get_participant_last_sync_timestamp(user_id, campaign_id):
    cur = conn.cursor()
    cur.execute('select max(sync_timestamp) from et_data_source_stats_maps where user_id=%s and campaign_id=%s;', (
        user_id,
        campaign_id
    ))
    last_sync_timestamp = cur.fetchone()[0]
    cur.close()
    return last_sync_timestamp


def bind_participant_to_campaign(user_id, campaign_id):
    cur = conn.cursor()
    cur.execute('select campaign_id from et_users where id=%s;', (user_id,))
    old_campaign_id = cur.fetchone()[0]
    if old_campaign_id is not None and old_campaign_id == campaign_id:
        cur.close()
        return False  # already bound
    cur.execute('select * from et_campaign_to_user_maps where user_id=%s and campaign_id=%s;', (
        user_id,
        campaign_id
    ))
    row = cur.fetchone()
    new_binding = row is None
    if new_binding:
        cur.execute('insert into et_campaign_to_user_maps(user_id, campaign_id, join_timestamp)  values (%s,%s,%s);', (
            user_id,
            campaign_id,
            utils.get_timestamp_ms()
        ))
        campaign = get_campaign_by_id(campaign_id=campaign_id)
        configurations = json.loads(s=campaign[4])
        cur = conn.cursor()
        for config_json in configurations:
            data_source_id = config_json['data_source_id']
            cur.execute('insert into et_data_source_stats_maps(user_id, campaign_id, data_source_id) values(%s,%s,%s)', (
                user_id,
                campaign_id,
                data_source_id
            ))
    cur.execute('update et_users set campaign_id = %s where id=%s;', (
        campaign_id,
        user_id
    ))
    cur.close()
    conn.commit()
    return new_binding


def get_campaign_start_timestamp(campaign_id):
    cur = conn.cursor()
    cur.execute('select start_timestamp from et_campaigns where id=%s;', (campaign_id,))
    campaign_start_timestamp = cur.fetchone()[0]
    cur.close()
    return campaign_start_timestamp


def campaign_has_started(campaign_id):
    return utils.get_timestamp_ms() >= get_campaign_start_timestamp(campaign_id=campaign_id)


def is_participant_bound_to_campaign(user_id, campaign_id):
    cur = conn.cursor()
    cur.execute('select * from et_campaign_to_user_maps where user_id=%s and campaign_id=%s;', (
        user_id,
        campaign_id
    ))
    row = cur.fetchone()
    cur.close()
    return row is not None


def create_or_update_campaign(campaign_id, creator_id, name, notes, configurations, start_timestamp, end_timestamp):
    cur = conn.cursor()
    # create campaign record
    cur.execute('select * from et_campaigns where id=%s;', (campaign_id,))
    campaign = cur.fetchone()
    if campaign is not None:
        # update existing if the owner made the request
        if creator_id == campaign[1]:
            # update campaigns table
            cur.execute('update et_campaigns set creator_id = %s, name = %s, notes = %s, config_json = %s, start_timestamp = %s, end_timestamp = %s where id=%s;', (
                creator_id,
                name,
                notes,
                configurations,
                start_timestamp,
                end_timestamp,
                campaign_id
            ))
            # update stats table
            cur.execute('select user_id from et_campaign_to_user_maps where campaign_id=%s;', (campaign_id,))
            user_rows = cur.fetchall()
            if user_rows is not None:
                new_configurations = json.loads(s=configurations)
                new_data_source_ids = []
                for old_config_json in new_configurations:
                    for user_row in user_rows:
                        user_id = user_row[0]
                        old_data_source_id = old_config_json['data_source_id']
                        cur.execute('insert into et_data_source_stats_maps(user_id, campaign_id, data_source_id) values(%s,%s,%s) on conflict do nothing;', (
                            user_id,
                            campaign_id,
                            old_data_source_id
                        ))
                        new_data_source_ids += [old_data_source_id]
                old_configurations = json.loads(s=campaign[4])
                for old_config_json in old_configurations:
                    old_data_source_id = old_config_json['data_source_id']
                    if old_data_source_id not in new_data_source_ids:
                        cur.execute('delete from et_data_source_stats_maps where campaign_id=%s and data_source_id=%s;', (campaign_id, old_data_source_id))
    else:
        # create new campaign
        cur.execute('insert into et_campaigns(creator_id, name, notes, config_json, start_timestamp, end_timestamp) values (%s,%s,%s,%s,%s,%s) returning id;', (
            creator_id,
            name,
            notes,
            configurations,
            start_timestamp,
            end_timestamp
        ))
        new_campaign_id = cur.fetchone()[0]
        # create sensor data table for the campaign
        cur.execute(
            '''
            create table if not exists et_campaign_{0}_data
            (
                user_id     integer references et_users (id)        on delete cascade,
                timestamp   bigint,
                data_source_id integer references et_data_sources (id) on delete cascade,
                values      varchar not null
            );
            create index et_campaign_{0}_data_idx on et_campaign_{0}_data(user_id, timestamp);
            '''.format(new_campaign_id)
        )
    cur.close()
    conn.commit()


def delete_campaign(campaign_id):
    cur = conn.cursor()
    cur.execute('drop table et_campaign_{0}_data;'.format(campaign_id))
    cur.execute('update et_users set campaign_id=null where campaign_id=%s;', (campaign_id,))
    cur.execute('delete from et_campaign_to_user_maps where campaign_id=%s;', (campaign_id,))
    cur.execute('delete from et_campaigns where id=%s;', (campaign_id,))
    cur.close()
    conn.commit()


def get_campaigns(creator_id=None):
    cur = conn.cursor()
    if creator_id is None:
        cur.execute('select * from et_campaigns;')
    else:
        cur.execute('select * from et_campaigns where creator_id=%s;', (creator_id,))
    rows = cur.fetchall()
    cur.close()
    conn.commit()
    return rows


def get_campaigns_participant_count(campaign_id):
    cur = conn.cursor()
    cur.execute('select count(*) from et_campaign_to_user_maps where campaign_id=%s;', (campaign_id,))
    row = cur.fetchone()
    cur.close()
    return row[0]


def get_campaign_by_id(campaign_id):
    cur = conn.cursor()
    cur.execute('select * from et_campaigns where id=%s;', (campaign_id,))
    row = cur.fetchone()
    cur.close()
    conn.commit()
    return row


def update_sync_timestamp(user_id, campaign_id, data_source_id, sync_timestamp):
    cur = conn.cursor()
    cur.execute('select sync_timestamp from et_data_source_stats_maps where user_id=%s and campaign_id=%s and data_source_id=%s;', (
        user_id,
        campaign_id,
        data_source_id
    ))
    prev_timestamp = cur.fetchone()[0]
    cur.execute("update et_data_source_stats_maps set sync_timestamp=%s where user_id=%s and campaign_id=%s and data_source_id=%s;", (
        max(sync_timestamp, prev_timestamp),
        user_id,
        campaign_id,
        data_source_id
    ))
    cur.close()
    conn.commit()


def update_user_heartbeat_timestamp(user_id):
    cur = conn.cursor()
    cur.execute("update et_users set last_heartbeat_timestamp = %s where id=%s;", (
        utils.get_timestamp_ms(),
        user_id
    ))
    cur.close()
    conn.commit()


def data_source_exists(data_source_id):
    cur = conn.cursor()
    cur.execute("select * from et_data_sources where id=%s;", (data_source_id,))
    row = cur.fetchone()
    cur.close()
    return row is not None


def store_data_record(user_id, timestamp_ms, data_source_id, values):
    campaign_id = get_participants_current_campaign_id(user_id=user_id)
    if not data_source_exists(data_source_id=data_source_id) or campaign_id is None or get_campaign_by_id(campaign_id=campaign_id) is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute('insert into et_campaign_{0}_data(user_id, timestamp, data_source_id, values) values (%s,%s,%s,%s);'.format(campaign_id), (
            user_id,
            timestamp_ms,
            data_source_id,
            values
        ))
        cur.execute('update et_data_source_stats_maps set amount_of_samples = amount_of_samples + 1 where user_id=%s and campaign_id=%s and data_source_id=%s;', (
            user_id,
            campaign_id,
            data_source_id
        ))
        cur.close()
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as e:
        print('db_mgr.store_data', e)
        return False


def store_direct_message(src_user_id, trg_user_id, subject, content):
    try:
        cur = conn.cursor()
        cur.execute("insert into et_direct_messages(src_user_id, trg_user_id, timestamp, subject, content)  values (%s,%s,%s,%s,%s);", (
            src_user_id,
            trg_user_id,
            utils.get_timestamp_ms(),
            subject,
            content
        ))
        cur.close()
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as e:
        print('db_mgr.store_direct_message', e)
        return False


def get_participants_amount_of_data(user_id, campaign_id):
    cur = conn.cursor()
    cur.execute('select sum(amount_of_samples) from et_data_source_stats_maps where user_id=%s and campaign_id=%s;', (
        user_id,
        campaign_id
    ))
    row = cur.fetchone()
    cur.close()
    return row[0]


def get_participants_stats_per_data_source(user_id, campaign):
    configurations = json.loads(s=campaign[4])
    res = []
    cur = conn.cursor()
    for config_json in configurations:
        data_source_id = config_json['data_source_id']
        cur.execute('select amount_of_samples, sync_timestamp from et_data_source_stats_maps where user_id=%s and campaign_id=%s and data_source_id=%s;', (
            user_id,
            campaign[0],
            data_source_id
        ))
        stat = cur.fetchone()
        res += [(data_source_id, stat[0], stat[1])]
    cur.close()
    return res


def get_next_100_filtered_data(user_id, campaign, from_timestamp, data_source_id):
    cur = conn.cursor()
    if data_source_id == -1:
        if from_timestamp == -1:
            cur.execute('select * from (select * from et_campaign_{0}_data where user_id=%s) as user_data order by timestamp desc limit(100);'.format(campaign[0]), (user_id,))
            rows = cur.fetchall()
            more_data_available = len(rows) == 100
            if more_data_available:
                cur.execute('select exists(select 1 from et_campaign_{0}_data where user_id=%s and timestamp>%s);'.format(campaign[0]), (
                    user_id,
                    rows[0][1]
                ))
                more_data_available = cur.fetchone()[0]
        else:
            cur.execute('select * from et_campaign_{0}_data where user_id=%s and timestamp>%s order by timestamp limit(100);'.format(campaign[0]), (
                user_id,
                from_timestamp,
            ))
            rows = cur.fetchall()
            more_data_available = len(rows) == 100
            if more_data_available:
                cur.execute('select exists(select 1 from et_campaign_{0}_data where user_id=%s and timestamp>%s);'.format(campaign[0]), (
                    user_id,
                    rows[len(rows) - 1][1]
                ))
                more_data_available = cur.fetchone()[0]
    else:
        if from_timestamp == -1:
            cur.execute('select * from (select * from et_campaign_{0}_data where user_id=%s and data_source_id=%s) as user_data order by timestamp limit(100);'.format(campaign[0]), (
                user_id,
                data_source_id
            ))
            rows = cur.fetchall()
            more_data_available = len(rows) == 100
            if more_data_available:
                cur.execute('select exists(select 1 from et_campaign_{0}_data where user_id=%s and timestamp>%s);'.format(campaign[0]), (
                    user_id,
                    rows[len(rows) - 1][1]
                ))
                more_data_available = cur.fetchone()[0]
        else:
            cur.execute('select * from (select * from et_campaign_{0}_data where user_id=%s and timestamp>%s and data_source_id=%s) as user_data order by timestamp limit(100);'.format(campaign[0]), (
                user_id,
                from_timestamp,
                data_source_id
            ))
            rows = cur.fetchall()
            more_data_available = len(rows) == 100
            if more_data_available:
                cur.execute('select exists(select 1 from et_campaign_{0}_data where user_id=%s and timestamp>%s);'.format(campaign[0]), (
                    user_id,
                    rows[len(rows) - 1][1]
                ))
                more_data_available = cur.fetchone()[0]
    cur.close()
    return rows, more_data_available


def get_filtered_data(user_id, campaign, data_source_id, from_timestamp, till_timestamp):
    cur = conn.cursor()
    cur.execute('select * from et_campaign_{0}_data where user_id=%s and data_source_id=%s and timestamp>%s and timestamp<%s order by timestamp;'.format(campaign[0]), (
        user_id,
        data_source_id,
        from_timestamp,
        till_timestamp
    ))
    rows = cur.fetchall()
    cur.close()
    return rows


def get_unread_direct_messages(user_id):
    cur = conn.cursor()
    cur.execute("select * from et_direct_messages where trg_user_id=%s and read=FALSE;", (user_id,))
    rows = cur.fetchall()
    cur.execute("update et_direct_messages set read=TRUE where trg_user_id=%s;", (user_id,))
    cur.close()
    conn.commit()
    return rows


def get_unread_notifications(user_id):
    cur = conn.cursor()
    cur.execute("select * from et_notifications where trg_user_id=%s and read=FALSE;", (user_id,))
    rows = cur.fetchall()
    cur.execute("update et_notifications set read=TRUE where trg_user_id=%s;", (user_id,))
    cur.close()
    conn.commit()
    return rows


def create_data_source(creator_id, name, icon_name):
    cur = conn.cursor()
    cur.execute("insert into et_data_sources(creator_id, name, icon_name) values (%s,%s,%s);", (
        creator_id,
        name,
        icon_name
    ))
    cur.close()
    conn.commit()


def get_data_source_by_name(name):
    cur = conn.cursor()
    cur.execute("select * from et_data_sources where name=%s;", (name,))
    row = cur.fetchone()
    cur.close()
    return row


def get_all_data_sources():
    cur = conn.cursor()
    cur.execute("select * from et_data_sources;")
    rows = cur.fetchall()
    cur.close()
    return rows
