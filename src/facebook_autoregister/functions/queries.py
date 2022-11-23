queries = {
    'insert_ready_accounts_query': '''
                                    INSERT INTO soc_accounts
                                    (soc_type, type, work, name, login, password, bdate, sessionid, work_hour, profile_id, priority, proxy_type, port, use_date)
                                    VALUES(2, \'FbUser222\', 0, %s %s, %s, %s, NOW(), %s, 0, \'4 madi\', 0, \'4 madi\', 0000, NOW())
                                   ''',
    'get_ready_accounts_query': '''
                                    SELECT first_name, last_name, phone_number, password, cookies
                                    FROM facebook_accounts
                                    WHERE status = 1 AND cookies IS NOT NULL
                                ''',
    'update_accounts_status_query': '''
                                        UPDATE proxies
                                        SET transfer_status = 1
                                        WHERE id = %s
                                    '''
}
