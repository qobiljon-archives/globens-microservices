import psycopg2
import json

conn = psycopg2.connect(
    host='127.0.0.1',
    database='easytrack_db',
    user='postgres',
    password='postgres'
)
print('connected to database')
cur = conn.cursor()

cur.execute('select * from et_campaigns;')
campaigns = cur.fetchall()
for campaign in campaigns:
    print('campaign id({0})'.format(campaign[0]))
    cur.execute('select user_id from et_campaign_to_user_maps where campaign_id=%s;', (campaign[0],))
    user_ids = [elem[0] for elem in cur.fetchall()]
    print('user ids : {0}'.format(user_ids))
    if len(user_ids) == 0:
        print('skipping empty campaign id({0}'.format(campaign[0], ))
        continue
    data_source_ids = [config['data_source_id'] for config in json.loads(s=campaign[4])]
    print('data source ids : {0}'.format(data_source_ids))
    for user_id in user_ids:
        for data_source_id in data_source_ids:
            print('campaign {0} user {1} data source {2}'.format(campaign[0], user_id, data_source_id))
            cur.execute('select timestamp from et_campaign_{0}_data where user_id=%s and data_source_id=%s order by timestamp desc limit 1;'.format(campaign[0]), (
                user_id,
                data_source_id
            ))
            last_sync_timestamp = cur.fetchone()
            last_sync_timestamp = 0 if last_sync_timestamp is None else last_sync_timestamp[0]
            cur.execute('update et_data_source_stats_maps set sync_timestamp=%s where user_id=%s and campaign_id=%s and data_source_id=%s;', (
                last_sync_timestamp,
                user_id,
                campaign[0],
                data_source_id
            ))

cur.close()
conn.commit()
conn.close()
print('database connection terminated')
