from time import sleep
import sys

class Rfid:
    '''
    simulate rfid.py to test the script on pc without rfid scanner
    '''
    def read_pipe(self, pipe: dict) -> None:
        '''
        put a fake id in a dict in arg
        '''
        sleep(1)
        pipe['id_badge'] = 63
        print('fake_badge', file=sys.stderr)