#!/usr/bin/env python
import mariadb
import os


import datetime

import warnings
import api_client
import sys

class ConnectionAutoClose:
    def __init__(self, conn_params):
        self.connection = mariadb.connect(**conn_params)
        self.cursor = self.connection.cursor()

    def __del__(self):
        try:
            self.connection.commit()
            self.connection.close()
        except Exception:
            pass

class Model:
    def __init__(self) -> None:
        self.check_with_badge_id = False
        self.conn_params = dict()
        self.api_client = api_client.APIClient()
        if os.name != "nt":

            self.conn_params["user"] = "root"
            self.conn_params["password"] = "0"
            self.conn_params["host"] = "localhost"
            self.conn_params["database"] = "timbreuse2022"
        else:
            self.conn_params["user"] = "root"
            self.conn_params["password"] = ""
            self.conn_params["host"] = "localhost"
            self.conn_params["port"] = 3306
            self.conn_params["database"] = "timbreuse2022"
        try:
            self.test_connect()
        except mariadb.ProgrammingError as E:
            if E.errno == 1049: # Unknown database
                self.create_structure()

    def create_structure(self):
        print('Model.create_structure', file=sys.stderr)
        database = self.conn_params['database']
        del self.conn_params['database']
        connection = self.get_connection_auto_close()
        with open('sql/createDB.sql') as sql:
            for line in sql.readlines():
                try: 
                    connection.cursor.execute(line)
                except mariadb.ProgrammingError:
                    # to ignore error end of file
                    print('Error create DB', file=sys.stderr)
        self.conn_params['database'] = database
        del connection

    def test_connect(self):
        connection = mariadb.connect(**self.conn_params)
        connection.cursor()
        print('connect', file=sys.stderr)
        
    def get_connection_auto_close(self):
        return ConnectionAutoClose(self.conn_params)

    def get_user_id_with_badge(self, badge_id)-> int:
        '''
        >>> model = Model()
        >>> model.get_user_id_with_badge(45)
        116
        '''
        sql = "SELECT `id_user` FROM `badge` WHERE `id_badge` = ?"
        connection = self.get_connection_auto_close()
        cursor = connection.cursor
        cursor.execute(sql, (badge_id, ))
        data = self.cursor_to_list(cursor)
        print(data, file=sys.stderr)
        if not any(data):
            return -1
        elif isinstance(data, int):
            return data
        try:
            return data[0][0]
        except IndexError:
            return data[0]
    
    def get_usernames(self, user_id) -> list:
        '''
        >>> model = Model()
        >>> model.get_usernames(116)
        ('Zéro-Six', 'Un-cinq')
        '''
        # to fix if offline and same id between user_write and user_sync
        print('get_usernames', file=sys.stderr)
        sql = 'SELECT `name`, `surname` FROM `user` WHERE `id_user` = ?;'
        connection = self.get_connection_auto_close()
        cursor = connection.cursor
        cursor.execute(sql, (user_id, ))
        data = self.cursor_to_tuple(cursor)
        return data
    
    def get_5_last_logs(self, badge_id) -> list:
        '''
        >>> model = Model()
        >>> type(model.get_5_last_logs(116))
        <class 'list'>
        '''
        user_id = self.get_user_id_with_badge(badge_id)
        sql = ('SELECT `date`, `inside`, `date_badge`, `date_modif`, '
               '`date_delete` FROM `log` WHERE `id_user` = ? OR '
               '`id_badge` = ? ORDER BY `date` DESC LIMIT 5;')
        connection = self.get_connection_auto_close()
        cursor = connection.cursor
        cursor.execute(sql, (user_id, badge_id))
        data = self.cursor_to_list(cursor)

        # in test do not close otherside
        del connection

        return data

    def find_user_info(self, pipe: dict) -> None:
        user_id = self.get_user_id_with_badge(pipe['id_badge'])
        if user_id is None:
            return
        pipe['name'], pipe['surname'] = self.get_usernames(user_id)
        five_logs = self.get_5_last_logs(pipe['id_badge'])
        pipe['log'] = self.cursor_to_dict_in_list(('date', 'inside',
                'date_badge', 'date_modif', 'date_delete'), five_logs)
        # to refactory
        self.read_work_time(pipe)
    
    @classmethod
    def is_deleted_log(cls, log):
        return log['date_delete'] is not None

    def read_work_time(self, pipe: dict) -> None:
        '''
        >>> model = Model()
        >>> pipe = dict()
        >>> pipe['id_badge'] = 47
        >>> model.read_work_time(pipe)
        '''
        print('read_work_time', file=sys.stderr)
        last_week, current_week = self.get_2_week_log(pipe)
        pipe['time_last_week'] = self.calcul_work_time(tuple(filter(
            lambda x:not self.is_deleted_log(x), last_week)))
        pipe['time_current_week'] = self.calcul_work_time(tuple(filter(
            lambda x:not self.is_deleted_log(x), current_week)))

        self.read_work_time_day(pipe, last_week, current_week)
    
    def call_insert_user(self, value:tuple):
        print('call_insert_user', file=sys.stderr)
        sql = 'CALL `insert_user`(?, ?);'
        self.execute_and_commit(sql, value)
        print('end call_insert_user', file=sys.stderr)
    
    def select_new_user(self, value) -> int:
        sql = ('SELECT `id_user` FROM `user_write` WHERE name=? AND surname=? '
               'ORDER BY `id_user` DESC;')
        connection = self.get_connection_auto_close()
        connection.cursor.execute(sql, value)
        data = self.cursor_to_list(connection.cursor)
        del connection
        return data[0][0]

    def call_insert_badge(self, value:tuple):
        '''
        call a stored procedure that insert badge
        '''
        print('call_insert_badge', file=sys.stderr)
        sql = 'CALL `insert_badge`(?, ?);'
        self.execute_and_commit(sql, value)
        print('end call_insert_badge', file=sys.stderr)

    def call_insert_log(self, value:tuple):
        '''
        call a stored procedure that insert log with datetime of the database
        >>> model = Model()
        >>> model.call_insert_log((42, True))
        '''
        print('call_insert_log', file=sys.stderr)
        sql = 'CALL `insert_log`(?, ?);'
        self.execute_and_commit(sql, value)
    
    def call_insert_sync_log(self, value):
        '''
        call a stored procedure that insert log in the sync_log table, 
        '''
        print('call_insert_sync_log', file=sys.stderr)
        sql = 'CALL `insert_sync_log`(?, ?, ?, ?, ?, ?, ?, ?);'
        print(value, file=sys.stderr)
        self.execute_and_commit(sql, value)

    def call_insert_sync_user_badge(self, data:tuple):
        '''
        call a stored procedure that insert user and badge in the user_sync
        and badge_sync table 
        >>> # model = Model()
        >>> # model.call_insert_sync_user_badge(tuple([49, 8, 'a', 'b']))
        '''
        print('call_insert_sync_badge', file=sys.stderr)
        sql = 'CALL `insert_users_and_badges`(?, ?, ?, ?);'
        self.execute_and_commit(sql, data)

    def call_insert_sync_user(self, data:tuple) -> None:
        '''
        call a strored procedure that insert user in user_sync table
        >>> # model = Model()
        >>> # model.call_insert_sync_user(tuple([2, 'Name', 'Surname']))
        >>> # model.call_insert_sync_badge(tuple([88282828, 2, 3]))
        '''
        print('call_insert_sync_user', file=sys.stderr)
        sql = 'CALL `insert_user_sync`(?, ?, ?, ?, ?);'
        self.execute_and_commit(sql, data)

    def call_insert_sync_badge(self, data:tuple) -> None:
        '''
        call a strored procedure that insert badge in badge_sync table
        >>> # model = Model()
        >>> # model.call_insert_sync_badge(tuple([88282828, 2, 3]))
        '''
        print('call_insert_sync_badge', file=sys.stderr)
        sql = 'CALL `insert_badge_sync`(?, ?, ?, ?, ?);'
        self.execute_and_commit(sql, data)

    # will be renamed in select_unsync_logs
    def call_get_unsync_log(self) -> list:
        '''
        select all logs in write table that is not in sync table,
        the return is like a tuple
        >>> model = Model()
        >>> print(type(model.call_get_unsync_log()))
        <class 'list'>
        '''
        print('call_get_unsync_log', file=sys.stderr)
        sql = ('SELECT `date`, `id_badge`, `inside`'
        'FROM `log_write`'
        'WHERE (`date`, `id_badge`, `inside`)'
        'NOT IN (SELECT `date`, `id_badge`, `inside` FROM `log_sync`);')
        connection = self.get_connection_auto_close()
        cursor = connection.cursor
        cursor.execute(sql)
        data = self.cursor_to_list(cursor)
        del connection
        return data

    def select_unsync_badges_and_users(self) -> list:
        '''
        select all badge id and user's names attach to badge id
        >>> model = Model()
        >>> cursor = model.select_unsync_badges_and_users()
        >>> type(cursor)
        <class 'list'>
        '''
        print('select_unsync_badges_and_users', file=sys.stderr)
        sql = ('SELECT `id_badge`, `name`, `surname` '
               'FROM `badge_write` LEFT OUTER JOIN `user_write` '
               'ON `badge_write`.`id_user` = `user_write`.`id_user` '
               'WHERE `id_badge` '
               'NOT IN (SELECT `id_badge` FROM `badge_sync` '
                    'WHERE `id_user` IS NOT NULL);')
        connection = self.get_connection_auto_close()
        cursor = connection.cursor
        cursor.execute(sql)
        data = self.cursor_to_list(cursor)
        del connection
        return data
    
    def send_logs(self):
        '''
        send all logs from the local database to the remote server
        '''
        print('send_logs', file=sys.stderr)
        for log in self.call_get_unsync_log():
            print(self.api_client.send_log(*log))
        print('end invoke_send_logs', file=sys.stderr)

    def send_unsync_badges_and_users(self):
        '''
        send all badge and user from the local database to the remote server
        '''
        print('send_unsync_badges_and_users', file=sys.stderr)
        for badge_and_names in self.select_unsync_badges_and_users():
            _, code = self.api_client.send_badge_and_user(*badge_and_names)
            print(code)


    def get_last_updated_datetime(self, table:str):
        '''
        >>> model = Model()
        >>> isinstance(model.get_last_updated_datetime('user'),
        ...             datetime.datetime)
        True
        '''
        print('get_last_updated_datetime', file=sys.stderr)
        sql = ('SELECT MAX(`date_modif`) '
               'FROM `{0}`;')
        sql = sql.format(table)
        connection = self.get_connection_auto_close()
        cursor = connection.cursor
        cursor.execute(sql)
        data = self.cursor_to_list(cursor)
        del connection
        try:
            last_datetime = data[0][0]
            if last_datetime is None:
                last_datetime = datetime.datetime.min
        except TypeError:
            last_datetime = datetime.datetime.min
        finally:
            print('last_datetime = ', last_datetime, file=sys.stderr)
            return last_datetime

    def get_last_updated_log_datetime(self):
        '''
        >>> model = Model()
        >>> isinstance(model.get_last_updated_log_datetime(),
        ...             datetime.datetime)
        True
        '''   
        return self.get_last_updated_datetime('log_sync')

    def invoke_receive_logs(self) -> None:
        '''
        receive all logs from remote server and insert in local database
        >>> model = Model()
        >>> model.invoke_receive_logs()
        '''
        print('model.invoke_receive_logs', file=sys.stderr)
        for log in self.api_client.receive_logs(
                self.get_last_updated_log_datetime()):
            print(log, file=sys.stderr)
            # insert one per one in local. can be better
            self.call_insert_sync_log(tuple(log.values()))
    
    def delete_badges_and_users_local(self) -> None:
        sql = 'CALL `delete_badge_and_user_write`;'
        self.execute_and_commit(sql)

            
    def invoke_receive_users(self) -> None:
        '''
        receive all user from remote server and insert in local database
        '''
        print('invoke_receive_users', file=sys.stderr)
        for user in self.api_client.receive_users(
                self.get_last_updated_datetime('user_sync')):
            print(user, file=sys.stderr)
            # insert one per one in local. can be better
            self.call_insert_sync_user(tuple(user.values()))
    
    def invoke_receive_badges(self) -> None:
        '''
        receive all badge from remote server and insert in local database
        >>> model = Model()
        >>> model.invoke_receive_users()
        >>> model.invoke_receive_badges()
        '''
        print('invoke_receive_badges', file=sys.stderr)
        for badge in self.api_client.receive_badges(
                self.get_last_updated_datetime('badge_sync')):
            print(badge, file=sys.stderr)
            # insert one per one in local. can be better
            self.call_insert_sync_badge(tuple(badge.values()))

    def execute_and_commit(self, sql, value:tuple=()):
        connection = self.get_connection_auto_close()
        connection.cursor.execute(sql, value)
        del connection

    @staticmethod
    def cursor_to_dict_in_list(select_name: tuple,
                               cursor: mariadb.Connection.cursor) -> list:
        l = list()
        for t in cursor:
            l.append(dict(zip(select_name, t)))
        return l

    @staticmethod
    def cursor_to_tuple(cursor: mariadb.Connection.cursor) -> tuple:
        l = list()
        for i in cursor:
            for j in i:
                l.append(j)
        return tuple(l)

    @staticmethod
    def cursor_to_list(cursor: mariadb.Connection.cursor) -> list:
        l = list()
        for i in cursor:
            l.append(i)
        return l

    @classmethod
    def calcul_work_time(cls, logs: tuple):
        print('calcul_work_time', file=sys.stderr)
        print(logs, file=sys.stderr)
        time = datetime.timedelta()
        date_in = None
        for log in logs[::-1]:
            if bool(log['inside']):
                if date_in is None:
                    date_in = log['date']
            elif date_in is not None:
                if date_in.day == log['date'].day: # ignore time with forgeting 
                    # outlog in the end of last day
                    # to text day on multi day with forteing the last
                    # first log of next day can bug
                    time += log['date'] - date_in
                date_in = None
        return time
    
    @classmethod
    def isolate_week(cls, logs: list)-> tuple:
        print('isolate_week', file=sys.stderr)
        current_week = list()
        last_week = list()
        last_monday = cls.find_last_monday(datetime.date.today())

        for log in logs:
            if cls.find_last_monday(log['date']) == last_monday:
                current_week.append(log)
            else:
                last_week.append(log)
        return tuple(last_week), tuple(current_week)

    @staticmethod
    def find_last_monday(date, n=0) -> datetime.date:
        '''
        n=0 the last monday (monday of the current week if monday is the first 
        day of the week).
        n=1 the monday before the last monday 
        '''
        print('find_last_monday', date, file=sys.stderr)
        try:
            return date.date() - datetime.timedelta(date.weekday() + 7*n)
        except:
            return date - datetime.timedelta(date.weekday() + 7*n)
    
    @staticmethod
    def is_same_day(date: datetime.date, date2: datetime.date) -> bool:
        print('is_same_day', file=sys.stderr)
        return ((date.day == date2.day) and (date.month == date2.month) and
                (date.year == date2.year))
        
    @classmethod
    def isolate_day(cls, logs:list) -> tuple:
        '''
        return a list with a list for each day.
        [id_day][id_log_in_the_day][key_of_property ex date, inside…]
        '''
        logs_per_day = list()
        logs_per_day.append(list())
        for log in logs:
            if len(logs_per_day[0]) == 0:
                logs_per_day[0].append(log)
            elif cls.is_same_day(log['date'], logs_per_day[-1][0]['date']):
                logs_per_day[-1].append(log)
            else:
                logs_per_day.append(list())
                logs_per_day[-1].append(log)
        return tuple(logs_per_day)

    @classmethod
    def get_date_and_work_time_day(cls, day_logs):
        try:
            print('model.get_work_time_day', file=sys.stderr)
            return (day_logs[0]['date'].date(), cls.calcul_work_time(day_logs))
        except IndexError:
            return None

    @classmethod
    def get_date_and_work_time_day_without_deleted(cls, day_logs):
        print('get_date_and_work_time_day_without_deleted', file=sys.stderr)
        filtered_logs = tuple(filter(lambda log: not cls.is_deleted_log(log),
                                day_logs))
        return cls.get_date_and_work_time_day(filtered_logs)

    def read_work_time_day(self, pipe:dict, last_week, current_week) -> None:
        '''
        add in dictionary in arg the date and sum work
        is a tuple. in each index there are a tuple with date [0] and sum time 
        work of the day [1]
        '''
        print('read_work_time_day', file=sys.stderr)
        pipe['last_week'] = self.isolate_day(last_week)
        pipe['current_week'] = self.isolate_day(current_week)
        pipe['day_last_week'] = tuple(map(
                self.get_date_and_work_time_day_without_deleted,
                pipe['last_week']))
        pipe['day_current_week'] = tuple(map(
                self.get_date_and_work_time_day_without_deleted,
                pipe['current_week']))

    def get_2_week_log(self, pipe:dict) -> tuple:
        '''
        >>> model = Model()
        >>> pipe = dict()
        >>> pipe['id_badge'] = 47
        >>> r = model.get_2_week_log(pipe)
        >>> isinstance(r, tuple)
        True
        '''
        id_user = self.get_user_id_with_badge(pipe['id_badge'])
        old_last_monday = self.find_last_monday(datetime.date.today(), 1)
        sql = ('SELECT `date`, `inside`, `date_badge`, `date_modif`, '
               '`date_delete` FROM `log` WHERE (`id_badge` = ? OR '
               '`id_user` = ?) AND `date` >= ? ORDER BY `date` DESC;')
        connection = self.get_connection_auto_close()
        cursor = connection.cursor
        cursor.execute(sql, (pipe['id_badge'], id_user, old_last_monday))
        names = ('date', 'inside', 'date_badge', 'date_modif', 'date_delete')
        two_week_log = self.cursor_to_dict_in_list(names, cursor)
        connection.connection.close()
        del(connection)
        return self.isolate_week(two_week_log)

    def invoke_new_user(self, pipe: dict):
        print('invoke_new_user', file=sys.stderr)
        value = (pipe['name'], pipe['surname'])
        print(value, file=sys.stderr)
        self.call_insert_user(value)
        user_id = self.select_new_user(value)
        print('user id', user_id, file=sys.stderr)
        value = (pipe['id_badge'], user_id)
        self.call_insert_badge(value)


def doctest():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    doctest()
