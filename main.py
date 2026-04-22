#!/usr/bin/env python
import os
import subprocess
import threading
import _thread
import view
try:
    import rfid
except:
    import fake_rfid as rfid
import model
import sys
import time

class App:
    '''
    controle view script, rfid script, model script
    '''

    def __init__(self):
        self.HAS_REMOTE_SERVER = True
        self.suspend_screen_time = 10*60
        self.view = None
        self.thread_view = None

        self.rfid = rfid.Rfid()

        self.pipe = dict()
        self.pipe['cancel'] = False
        self.reset_pipe()
        self.model = model.Model()
        self.thread_model_request = None
        self.thread_model_insert = None
        self.thread_model_new_user = None
        self.thread_wait_quit = threading.Thread(target=self.wait_quit,
                args=(self.pipe, ))
        self.thread_send_log = None
        self.thread_send_badges_and_users = None
        self.thread_receive_log = None
        self.thread_receive_users = None
        self.thread_receive_badges = None
        self.thread_receive_event_logs = None
        self.thread_apply_event_logs = None
        self.thread_delete_badges_and_users = None
        self.thread_synchronize_user_badge_log_with_remote = None
        self.thread_Invoke_synchronize_before_rfid = None
        self.thread_Invoke_synchronize_after_rfid = None

    def load(self):
        self.view = view.View()
        self.thread_view = threading.Thread(target=self.view.load)
        self.turn_off_screen_interval(self.suspend_screen_time)
        self.thread_view.start()
        self.thread_wait_quit.start()
        self.view.read_pipe(self.pipe)

        if self.HAS_REMOTE_SERVER:
            self.invoke_join_thread(
                'thread_synchronize_user_badge_log_with_remote',
                self.synchronize_user_badge_log_with_remote)
                
        
        while True:
            self.update()

    def update(self):
        if self.HAS_REMOTE_SERVER:
            self.invoke_thread('thread_Invoke_synchronize_before_rfid',
                self.Invoke_synchronize_before_rfid)
        self.do_rfid()
        if self.HAS_REMOTE_SERVER:
            if self.handle_deleted_remote_badge():
                self.reset()
                return
        if self.HAS_REMOTE_SERVER:
            self.invoke_thread('thread_Invoke_synchronize_after_rfid',
                self.Invoke_synchronize_after_rfid)
        self.turn_on_screen()
        self.do_model_request()
        if self.is_unknown():
            self.view.do_unknown_badge_dict(self.pipe)
        else:
            self.view.do_select_scene_dict(self.pipe)

        self.wait_choice()
        if self.pipe['quit']:
            quit()
        if self.is_cancel():
            self.reset()
            return
        if self.pipe['new_user_valid']:
            self.invoke_join_thread('thread_model_new_user',
                self.model.invoke_new_user, (self.pipe.copy(), ))
            self.reset()
            return
        self.invoke_insert()
        self.view.do_wait_scene()
        self.reset()
    

    def invoke_insert(self):
        '''
        >>> main = App()
        >>> main.pipe = dict()
        >>> main.pipe['id_badge'] = 42
        >>> main.pipe['inside'] = True
        >>> main.invoke_insert()
        '''
        args = ((self.pipe['id_badge'], self.pipe['inside']), )
        self.invoke_join_thread('thread_model_insert',
            self.model.call_insert_log, args)
    
    def invoke_send_log(self) -> None:
        '''
        manage thread to send all new logs from local
        '''
        print('invoke_send_log', file=sys.stderr)
        self.safe_wait_thread(self.thread_send_log)
        self.thread_send_log = threading.Thread(
            target=self.model.send_logs)
        self.thread_send_log.start()
        self.thread_send_log.join()
    
    def invoke_send_unsync_badges_and_users(self) -> None:
        '''
        manage thread to send all new badges and users
        '''
        print('invoke_send_unsync_badges_and_users', file=sys.stderr)
        self.safe_wait_thread(self.thread_send_badges_and_users)
        self.thread_send_badges_and_users = threading.Thread(
            target=self.model.send_unsync_badges_and_users)
        self.thread_send_badges_and_users.start()
        self.thread_send_badges_and_users.join()


    def invoke_receive_logs(self) -> None:
        '''
        manage thread to receive all new logs from remote
        '''
        print('invoke_receive_logs', file=sys.stderr)
        self.safe_wait_thread(self.thread_receive_log)
        self.thread_receive_log = threading.Thread(
            target=self.model.invoke_receive_logs)
        self.thread_receive_log.start()
        self.thread_receive_log.join()

    def Invoke_synchronize_after_rfid(self):
        thread = threading.Thread(
                target=self.synchronize_user_badge_log_with_remote)
        self.safe_wait_thread(self.thread_Invoke_synchronize_before_rfid)
        thread.start()
        thread.join()

    def Invoke_synchronize_before_rfid(self):
        thread = threading.Thread(
                target=self.synchronize_user_badge_log_with_remote)
        self.safe_wait_thread(self.thread_Invoke_synchronize_after_rfid)
        thread.start()
        thread.join()

    def invoke_thread(self, thread:str, function, args=()):
        '''
        manage thread in safe way
        '''
        print('invoke_thread', 'thread', thread, 'function', function,
              file=sys.stderr)
        if self.safe_is_alive(getattr(self, thread)):
            return
        setattr(self, thread, threading.Thread(target=function, args=args))
        getattr(self, thread).start()

    def invoke_join_thread(self, thread:str, function:'function',
                           args:tuple=()):
        '''
        manage thread in procedural way
        '''
        print('invoke_join_thread', 'thread', thread, 'function', function,
              file=sys.stderr)
        self.safe_wait_thread(getattr(self, thread))
        print('args', args, file=sys.stderr)
        setattr(self, thread, threading.Thread(target=function, args=args))
        print('before start invoke_join_thread', 'thread', thread, 'function',
              function, file=sys.stderr)
        getattr(self, thread).start()
        print('before join invoke_join_thread', 'thread', thread, 'function',
              function, file=sys.stderr)
        getattr(self, thread).join()
        print('end invoke_join_thread', 'thread', thread, 'function', function,
              file=sys.stderr)

    @staticmethod
    def wait_quit(pipe):
        wait_thread = pipe['th_condition']
        wait_thread.acquire()
        while not pipe['quit']:
            wait_thread.wait()
        wait_thread.release()
        print('exit wait_quit', file=sys.stderr)
        _thread.interrupt_main() 

    def is_cancel(self):
        return self.pipe['cancel']

    @staticmethod
    def turn_on_screen() -> None:
        try:
            # do it only on the Raspberry Pi
            if os.name != 'nt':
                subprocess.run(['xset', 'dpms', 'force', 'on'])
        except Exception:
            pass

    @staticmethod
    def turn_off_screen_interval(interval: int) -> None:
        '''
        turn off screen after inactivity times
        Parameters:
            interval(int): interval in second off
        '''
        try:
            # do it only on the Raspberry Pi
            if os.name != 'nt':
                subprocess.run(['xset', 's', str(interval) + 's'])
        except Exception:
            pass

    def do_rfid(self):
        '''
        scanne rfid, put id in pipe
        with a thread
        side effect, pipe['id_badge'] is mutable
        '''
        print('do_rfid()', file=sys.stderr)
        self.thread_rfid = threading.Thread(target=self.rfid.read_pipe,
                                            args=(self.pipe, ))
        self.thread_rfid.start()
        self.thread_rfid.join()

    def do_model_request(self):
        '''
        read user data from database
        with a thread
        '''
        print('do_model_request()', file=sys.stderr)
        self.invoke_join_thread('thread_model_request', 
                                self.model.find_user_info, args=(self.pipe, ))
        print('end do_model_request', self.pipe, file=sys.stderr)

    def wait_modal_ack(self):
        while (not self.pipe.get('quit', False)
                and self.view is not None
                and self.view.current_scene == 'modal'):
            time.sleep(0.1)

    def handle_deleted_remote_badge(self) -> bool:
        """
        Retourne True si une suppression distante est detectee et geree.
        """
        check = self.model.check_badge_assignment_with_remote(self.pipe['id_badge'])
        if check['remote_exists']:
            return False

        if check['local_exists']:
            self.model.remove_local_badge_correspondance(self.pipe['id_badge'])
            user_name = check['local_user_name'] or 'cet utilisateur'
            texts = [
                f"Ce badge n'est plus attribue a {user_name}.",
                'Cette correspondance est supprimee egalement sur cet appareil.',
            ]
        else:
            texts = ["Ce badge n'est pas attribue a un utilisateur."]

        self.view.do_badge_sync_error(texts)
        self.wait_modal_ack()
        return True

    def safe_is_alive(self, thread):
        try:
            print('tread is alive', thread.is_alive(), file=sys.stderr)
            return thread.is_alive()
        except:
            return False

    def safe_wait_thread(self, thread):
        '''
        Wait (block the execution) the end of a thread.
        Check if the thread is running.
        '''
        if self.safe_is_alive(thread):
            thread.join()

    def wait_choice(self):
        wait_thread = self.pipe['th_condition']
        wait_thread.acquire()
        while ((self.pipe["inside"] == None) and (not self.is_cancel()) and
                (not self.pipe['new_user_valid']) and (not self.pipe['quit'])):
            wait_thread.wait()
            print('choice done', file=sys.stderr)
            wait_thread.release()

    def reset_pipe(self):
        self.pipe = dict()
        self.pipe["id"] = None
        self.pipe["date"] = None
        self.pipe["inside"] = None
        self.pipe["log"] = list()
        self.pipe["name"] = ''
        self.pipe["surname"] = ''
        self.pipe['id_badge'] = None
        self.pipe['cancel'] = False
        self.pipe['new_user_valid'] = False
        self.pipe['th_condition'] = threading.Condition()
        self.pipe['quit'] = False

    def reset(self):
        print('reset()', file=sys.stderr)
        self.reset_pipe()

    def __del__(self):
        pass

    def is_unknown(self):
        print('name', self.pipe['name'], file=sys.stderr)
        return self.pipe['name'] == ''

    def get_threads_and_functions_list(self):
        threads_and_functions = list()
        threads_and_functions.append(('thread_receive_event_logs',
                                self.model.invoke_receive_event_logs))
        threads_and_functions.append(('thread_apply_event_logs',
                                self.model.apply_event_logs))
        threads_and_functions.append(('thread_send_badges_and_users',
                                self.model.send_unsync_badges_and_users))
        threads_and_functions.append(('thread_send_log', self.model.send_logs))
        threads_and_functions.append(('thread_receive_users',
                                self.model.invoke_receive_users))
        threads_and_functions.append(('thread_receive_badges',
                                self.model.invoke_receive_badges))
        threads_and_functions.append(('thread_receive_log',
                                self.model.invoke_receive_logs))
        threads_and_functions.append(('thread_delete_badges_and_users',
                                self.model.delete_badges_and_users_local))
        return threads_and_functions

    def synchronize_user_badge_log_with_remote(self):
        print('synchronize_user_badge_log_with_remote', file=sys.stderr)
        for thread, function in self.get_threads_and_functions_list():
            self.invoke_join_thread(thread, function)

def main():
    app = App()
    app.load()

def doctest():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    main()
