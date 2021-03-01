from gb_grpcs import gb_service_pb2 as gb

db_settings = {
    'host': 'localhost',
    'database': 'globens_db',
    'user': 'postgres',
    'password': 'postgres'
}

db_conn = None

currency_enum2str_map = {
    gb.KRW: 'KRW',
    gb.USD: 'USD',
    gb.UZS: 'UZS',
    gb.RUB: 'RUB'
}
currency_str2enum_map = {currency_enum2str_map[k]: k for k in currency_enum2str_map}

product_type_enum2str_map = {
    gb.FILE_DOWNLOADABLE: 'downloadable files',
    gb.FILE_STREAMED: 'streamed files',
    gb.SCHEDULED_FACE_TO_FACE: 'scheduled face-to-face meeting',
    gb.SCHEDULED_ONLINE_CALL: 'scheduled online call'
}
product_type_str2enum_map = {currency_enum2str_map[k]: k for k in currency_enum2str_map}
