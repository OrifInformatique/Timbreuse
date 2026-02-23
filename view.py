from itertools import product
import abc
import pygame
import pygame_vkeyboard as vkboard
import sys
import os
import datetime
from model import Model
import warnings


class Button:
    '''
    button show with rect and unique color
    Keyword arguments:
    id -- is use for Table
    '''
    def __init__(self, screen: pygame.Surface, x, y, w, h,
                color=pygame.Color("#6c767e"), img: str = 'cancel',
                id=-1) -> None:
        print("Button.init", file=sys.stderr)
        self.screen = screen
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.id = id

        self.color = color
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.img = Loader.load_icon(img, pygame.Color('#f8f9fa'))
        
    @staticmethod
    def inside_button(screen: pygame.Surface) -> 'Button':

        cx, cy = screen.get_size()
        x = 7 * (cx / 12)
        y = 4 * (cy / 12)
        w = 4 * (cx / 12)
        h = 7 * (cy / 12)
        img = 'in'

        color = pygame.Color("#007bff")  # blue
        return Button(screen, x, y, w, h, color, img)

    @staticmethod
    def outside_button(screen: pygame.Surface) -> 'Button':

        cx, cy = screen.get_size()
        x = 1 * (cx / 12)
        y = 4 * (cy / 12)
        w = 4 * (cx / 12)
        h = 7 * (cy / 12)
        img = 'out'

        color = pygame.Color("#Dc3545")  # red
        return Button(screen, x, y, w, h, color, img)

    @staticmethod
    def log_button(screen: pygame.Surface) -> 'Button':
        cx, cy = screen.get_size()
        x = 9 * (cx / 12)
        y = 1 * (cy / 12)
        w = 2 * (cx / 12)
        h = 2 * (cy / 12)
        img = 'log'
        color = pygame.Color("#6c767e")  # gray
        return Button(screen, x, y, w, h, color, img)

    @staticmethod
    def cancel_button(screen: pygame.Surface) -> 'Button':

        cx, cy = screen.get_size()
        x = 1 * (cx / 12)
        y = 1 * (cy / 12)
        w = 2 * (cx / 12)
        h = 2 * (cy / 12)
        img = 'cancel'

        color = pygame.Color("#6c767e")  # gray
        return Button(screen, x, y, w, h, color, img)

    @staticmethod
    def return_button(screen: pygame.Surface) -> 'Button':

        cx, cy = screen.get_size()
        x = 1 * (cx / 12)
        y = 1 * (cy / 12)
        w = 2 * (cx / 12)
        h = 2 * (cy / 12)
        img = 'return'

        color = pygame.Color('#6c767e')  # off white 
        return Button(screen, x, y, w, h, color, img)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, self.rect, 0, 10)
        self.draw_img_center(screen)
    
    def draw_img_center(self, screen: pygame.Surface):
        screen.blit(self.img, (self.x + self.w/2 - self.img.get_width()/2,
                               self.y + self.h/2 - self.img.get_height()/2))

class ButtonText(Button):
    '''
    button with text image and color
    '''
    def __init__(self, screen: pygame.Surface, x, y, w, h,
                 color=pygame.Color("#6c767e"), img: str = 'cancel',
                 text: str = 't') -> None:
        super().__init__(screen, x, y, w, h, color, img)
        self.size = 30 
        self.text = Text(x + w/2, y + h - self.size - 20, self.size,
                         text, pygame.Color('white'), 'center')
    
    def draw(self, screen) -> None:
        super().draw(screen)
        self.text.draw(screen)

    @staticmethod
    def inside_button(screen: pygame.Surface) -> 'ButtonText':

        cx, cy = screen.get_size()
        x = 1 * (cx / 12)
        y = 4 * (cy / 12)
        w = 4 * (cx / 12)
        h = 7 * (cy / 12)
        img = 'in'
        text = 'Entrée'

        color = pygame.Color("#007bff")  # blue
        return ButtonText(screen, x, y, w, h, color, img, text)

    @staticmethod
    def outside_button(screen: pygame.Surface) -> 'ButtonText':

        cx, cy = screen.get_size()
        x = 7 * (cx / 12)
        y = 4 * (cy / 12)
        w = 4 * (cx / 12)
        h = 7 * (cy / 12)
        img = 'out'
        text = 'Sortie'

        color = pygame.Color("#Dc3545")  # red
        return ButtonText(screen, x, y, w, h, color, img, text)



class Scene(abc.ABC):
    '''
    scene containt text and button
    '''

    def __init__(self, screen:pygame.Surface, view:'View') -> None:
        if View.debug:
            print("init Scene", file=sys.stderr)

        self.screen = screen
        self.view = view

    def update(self) -> None:
        '''
        is called each frame
        '''
        pass

    def draw(self) -> None:
        '''
        is called each frame. containt function to show
        '''
        pass


class SceneTime(Scene, abc.ABC):
    '''
    'abstrat class', active timer that cancel the session
    '''
    def __init__(self, screen: pygame.Surface, view: 'View') -> None:
        super().__init__(screen, view)
        self.entry_time = datetime.datetime.today()

    def update(self) -> None:
        '''
        is called each frame
        '''
        super().update()
        self.do_cancel()

    def check_time(self, minute: int) -> bool:
        '''
        check time with now and entry_time proprety 
        '''
        return (datetime.datetime.today() - self.entry_time >
            datetime.timedelta(minutes=minute))

    def do_cancel(self) -> None:
        if self.check_time(1):
            self.view.cancel()

    def reset_entry_time(self) -> None:
        self.entry_time = datetime.datetime.today()


class SceneSelect(SceneTime):
    '''
    is the scene with buttons
    '''

    def __init__(self, screen: pygame.Surface, view: 'View'):
        if View.debug:
            print("SceneSelect load", file=sys.stderr)
        super().__init__(screen, view)

        self.choice = dict()

        self.buttons = list()
        self.buttons.append(ButtonText.inside_button(self.screen)) # blue right
        self.buttons.append(ButtonText.outside_button(self.screen))  # red left
        self.buttons.append(Button.log_button(self.screen))  # red left
        self.buttons.append(Button.cancel_button(self.screen))  # red left
        self.texts = list()
        self.texts.append(Text(10, 5, 30, '', pygame.Color('black')))

    def update(self):
        super().update()
        self.do_press_button()
        try:
            # must be optimised, not all frame
            self.texts[0](View.pipe['surname'] + ' ' + View.pipe['name'])
        except KeyboardInterrupt:
            exit()
        except:
            pass

    def do_press_button(self):
        if (self.buttons[0].rect.collidepoint(pygame.mouse.get_pos()) and
                self.view.mouse.release('left')):
            if View.debug:
                print("blue right pressed", file=sys.stderr)
            self.take_choice_dict(True, View.pipe)

        if (self.buttons[1].rect.collidepoint(pygame.mouse.get_pos()) and
                self.view.mouse.release('left')):
            if View.debug:
                print("red left pressed", file=sys.stderr)
            self.take_choice_dict(False, View.pipe)

        if (self.buttons[2].rect.collidepoint(pygame.mouse.get_pos()) and
                self.view.mouse.release('left')):
            self.reset_entry_time()
            # access parent instance
            self.view.do_log_scene(View.pipe['log'])

        if (self.buttons[3].rect.collidepoint(pygame.mouse.get_pos()) and
                self.view.mouse.release('left')):
            # access parent instance
            self.view.cancel()

    def draw(self):
        super().draw()
        for button in self.buttons:
            button.draw(self.screen)
        for text in self.texts:
            text.draw(self.screen)

    @staticmethod
    def take_choice(choice: bool) -> tuple:
        '''
        return arg and date time
        '''
        return (choice, datetime.datetime.today())

    @classmethod
    def take_choice_dict(cls, choice: bool, pipe: dict) -> None:
        '''
        get the choice in a dict in args
        '''
        pipe["inside"], pipe["date"] = cls.take_choice(choice)

        # unlock the main thread in main.py
        pipe['th_condition'].acquire()
        pipe['th_condition'].notify_all()
        pipe['th_condition'].release()


class SceneWait(Scene):
    '''
    is the waiting screen with time
    '''

    def __init__(self, screen: pygame.Surface, view: 'View'):

        super().__init__(screen, view)

        self.texts = list()
        self.texts.append(Text(10, 10, 30, "Attente d’un badge RFID"))
        self.texts.append(Text(10, 40, 30, ""))
        self.body = Body('logo')

    def update(self):
        super().update()
        self.texts[1].text = str(datetime.datetime.today())[0:-7]
        for txt in self.texts:
            txt.update()
        self.body.update(self.screen)

    def draw(self):
        super().draw()
        for txt in self.texts:
            txt.draw(self.screen)
        self.body.draw(self.screen)

class Body:
    '''
    is use for bounced logo
    '''
    def __init__(self, img: str):
        self.img = Loader.load_img(img)
        self.rect = self.img.get_rect() 
        self.speed = pygame.Vector2(1, 1)
    
    def update(self, screen: pygame.Surface):
        '''
        is call each frame when is on the screen
        '''
        cx, cy = screen.get_size()
        self.rect = self.rect.move(self.speed)
        if self.rect.left < 0 or self.rect.right > cx:
            self.speed.x = -self.speed.x
        if self.rect.top < 0 or self.rect.bottom > cy:
            self.speed.y = -self.speed.y
    
    def draw(self, screen: pygame.Surface):
        '''
        is call each frame when is on the screen, contain showing funcion
        '''
        screen.blit(self.img, self.rect)

class SceneLog(SceneTime):
    '''
    scene show 5 last logs
    '''

    def __init__(self, screen: pygame.Surface, view: 'View') -> None:
        super().__init__(screen, view)
        self.texts = list()
        self.size_text = 30

        self.buttons = list()
        self.buttons.append(Button.return_button(screen))
        cx, cy = screen.get_size()
        self.buttons.append(Button(screen, 9 * cx / 12, 1 * cy / 12,
                                   2 * cx / 12, 2 * cy / 12, img='more'))

    @staticmethod
    def is_deleted_log_text(log):
        return log['date_delete'] is not None

    @classmethod
    def get_deleted_log_text(cls, log) -> str:
        print('get_deleted_log_text', file=sys.stderr)
        try:
            if cls.is_deleted_log_text(log):
                return cls.get_text_with_chevron('supprimé')
            else:
                return ''
        except:
            return ''

    @classmethod
    def get_site_log_text(cls, log) -> str:
        print('get_site_log_text', file=sys.stderr)
        try:
            if log['date_badge'] is None:
                return cls.get_text_with_chevron('site')
            else:
                return ''
        except:
            return ''

    @classmethod
    def get_modified_log_text(cls, log) -> str:
        print('get_modified_log_text', file=sys.stderr)
        try:
            if log['date_badge'] == log['date']:
                return ''
            else:
                return cls.get_text_with_chevron('modifié')
        except:
            return ''
        
    @staticmethod
    def get_text_with_chevron(text):
        return f'<{text}>'

    @classmethod
    def get_one_log_text(cls, log) -> str:
        print('get_one_log_text', file=sys.stderr)
        text = cls.get_deleted_log_text(log)
        if text != '':
            return ' ' + text
        text = cls.get_site_log_text(log)
        if text != '':
            return ' ' + text
        return ' ' + cls.get_modified_log_text(log)

    def set_text(self, index: int, log: dict, info: dict) -> None:
        x, y = info['x'], info['y']
        text_inside, text_outside = info['text_inside'], info['text_outside']

        
        # text_log = str(log['date'])[:-3] + ' ' + self.change_text_bool(
        #     log['inside'], text_inside, text_outside)

        text_log = str(log['date']) + ' ' + self.change_text_bool(
            log['inside'], text_inside, text_outside)
        
        text_log += self.get_one_log_text(log)
        
        self.texts.append(Text(x, y + index * self.size_text,
                            self.size_text, text_log, pygame.Color('black')))
        if self.is_deleted_log_text(log):
            self.texts[-1].strikethrough = True

    def set_texts(self, logs: list) -> None:
        print('SceneLog.set_texts', file=sys.stderr)
        info = dict()
        cx, cy = self.screen.get_size()
        info["x"] = 1 * cx / 12
        info["y"] = 4 * cy / 12
        info['text_inside'] = 'entrée'
        info['text_outside'] = 'sortie'

        self.texts = list()

        for index, log in enumerate(logs):
            self.set_text(index, log, info)

    @staticmethod
    def change_text_bool(b, text_true: str, text_false: str) -> str:
        return text_true if bool(b) else text_false

    def update(self):
        super().update()
        self.do_press_button()

    def do_press_button(self):
        if (self.view.mouse.release('left') and
                self.buttons[0].rect.collidepoint(pygame.mouse.get_pos())):
            self.reset_entry_time()
            # access parent instance
            self.view.current_scene = 'select'

        if (self.view.mouse.release('left') and
                self.buttons[1].rect.collidepoint(pygame.mouse.get_pos())):
            self.reset_entry_time()
            self.view.do_work_time()

    def draw(self):
        super().draw()
        for text in self.texts:
            text.draw(self.screen)

        for button in self.buttons:
            button.draw(self.screen)


class SceneWorkTime(SceneTime):
    '''
    scene with a table/grid that show dates and times
    '''
    def __init__(self, screen: pygame.Surface, view: 'View',
            week_str: str='current_week') -> None:
        super().__init__(screen, view)
        self.texts = list()
        self.size_text = 30
        self.buttons = list()
        self.buttons.append(Button.return_button(screen))
        if week_str == 'current_week':
            cx, cy = screen.get_size()
            self.buttons.append(Button(screen, 9 * cx / 12, 1 * cy / 12,
                                    2 * cx / 12, 2 * cy / 12, img='next'))
        self.tables = list()
        self.week_str = week_str

    def do_press_return_button(self) -> None:
        if (self.view.mouse.release('left') and
                self.buttons[0].rect.collidepoint(pygame.mouse.get_pos())):
            self.reset_entry_time()
            # access parent instance
            if self.week_str == 'current_week':
                self.view.current_scene = 'log'
            elif self.week_str == 'last_week':
                self.view.current_scene = 'time'
            # add reset timer

    def do_press_next_button(self) -> None:
        if (self.week_str == 'current_week' and self.view.mouse.release('left')
            and self.buttons[1].rect.collidepoint(pygame.mouse.get_pos())):
            self.reset_entry_time()
            # access parent instance
            self.view.do_work_time('last_time')
            # add reset timer

    def do_press_table_button(self) -> None:
        if self.view.mouse.release('left'):
            pressed_button = None
            for table in self.tables:
                pressed_button = table.get_press_button()                 
            if pressed_button is not None:
                self.reset_entry_time()
                self.do_modal_scene(pressed_button.id)

    @staticmethod
    def get_inside_label_log(log):
        if bool(log['inside']):
            return " entrée"
        else:
            return " sortie"

    # deprecated
    @staticmethod
    def get_dict_log_list(log:list) -> dict:
        warnings.warn("deprecated", DeprecationWarning)
        log_dict = dict()
        log_dict['date'] = log[0]
        log_dict['inside'] = log[1]
        log_dict['date_badge'] = log[2]
        log_dict['date_modif'] = log[3]
        log_dict['date_delete'] = log[4]
        return log_dict

    def get_text_modal_row(self, log):
        #text = str(log['date'])[:-3]
        text = str(log['date'])
        text += self.get_inside_label_log(log)
        text += SceneLog.get_one_log_text(log)
        return text

    def do_modal_scene(self, id: int) -> None:
        '''
        id is id of button on table
        '''
        print('SceneWorkTime.do_modal_scene', file=sys.stderr)
        date = View.pipe[f'day_{self.week_str}'][id][0]
        filtered_logs = tuple(filter(lambda day: Model.is_same_day(date,
            day[0]['date']), View.pipe[self.week_str]))[0]
        text_tuple = tuple(map(self.get_text_modal_row, filtered_logs)) 
        if self.week_str == 'current_week':
            time = 'time'
        else:
            time = 'last_time'
        self.view.scenes = 'modal', SceneModal(self.screen, self.view,
            text_tuple, time)
        self.view.current_scene = 'modal'
    
    @staticmethod
    def format_timedelta(timedelta: datetime.timedelta):
        hh, ss = divmod(timedelta.seconds, 3600)
        mm, ss = divmod(ss, 60)
        hh += timedelta.days*24
        return f"{hh}:{mm:02d}:{ss:02d}"

    def set_content(self):
        print('SceneWorkTime.set_content', file=sys.stderr)
        self.texts.clear()
        self.texts.append(list())
        self.texts[0].append('Date')
        self.texts.append(list())
        self.texts[1].append('Temps')
        self.texts.append(list())
        self.texts[2].append('Détail')
        if f'day_{self.week_str}' in View.pipe:
            for day in View.pipe[f'day_{self.week_str}']:
                # day[0] is date
                # day[1] is sum time
                try:
                    self.texts[0].append(str(day[0]))
                    self.texts[1].append(str(day[1]))
                    self.texts[2].append('detail')
                except TypeError:
                    pass
            self.texts[0].append('Total : ')
            self.texts[1].append(self.format_timedelta(View.pipe[
                    f'time_{self.week_str}']))
            self.set_table()
        print(self.texts, file=sys.stderr)
    
    def set_table(self):
        cx, cy = self.screen.get_size()
        x = 1 * cx / 12
        y = 4 * cy / 12
        w = 11 * cx / 12
        h = 8 * cy / 12
        self.tables.clear()
        self.tables.append(Table(x, y, w, h, self.texts))

    def update(self):
        super().update()
        self.do_press_return_button()
        self.do_press_next_button()
        self.do_press_table_button()

    def draw(self):
        super().draw()
#        for text in self.texts:
#            text.draw(self.screen)
        for table in self.tables:
            table.draw(self.screen)

        for button in self.buttons:
            button.draw(self.screen)

class Table:
    '''
    table/grid with content text or id of img that give a button
    '''
    def __init__(self, x, y , w, h, columns: list):
        print('Table.init', file=sys.stderr)
        self.size_text = 30
        self.pos = pygame.Vector2(x, y)
        self.size = pygame.Vector2(w, h - self.size_text) # pixel
        self.columns = columns # list of string
        self.update_scaling() # number element in row columns
        self.update_pixel_case() 
        self.buttons = list()
        self.texts = list()
        self.button_color = pygame.Color('#6c767e')
        self.set_content()

    def update_scaling(self):
        print('Table.update_scaling', file=sys.stderr)
        print(self.columns)
        len_columns = map(lambda row:len(row), self.columns)
        self.scaling = pygame.Vector2(len(self.columns), max(len_columns))
        print(self.scaling, file=sys.stderr)

    def update_pixel_case(self):
        print('Table.update_pixel_case', file=sys.stderr)
        self.pixel_case = pygame.Vector2(self.size.x / self.scaling.x,
                                         self.size.y / self.scaling.y)
        print(self.pixel_case, file=sys.stderr)

    def check_and_put_strikethrough(self, text:'Text') -> None:
        if '<supprimé>' in text.text:
            self.texts[-1].strikethrough = True

    def set_case_content(self, cursor, nb_line, text):
        if text in Loader.paths:
            self.buttons.append(Button(None, cursor.x, cursor.y,
                self.pixel_case.x * 8 / 12, self.pixel_case.y * 11 / 12,
                self.button_color, text, nb_line - 1)) 
        else:
            self.texts.append(Text(cursor.x, cursor.y, self.size_text, text))
            self.check_and_put_strikethrough(self.texts[-1])

    def set_column_content(self, cursor, colone): 
        # side effect on cursor
        for nb_line, text in enumerate(colone):
            self.set_case_content(cursor, nb_line, text)
            cursor.y += self.pixel_case.y

    def set_content(self):
        print("Table.set_content", file=sys.stderr)
        cursor = pygame.Vector2(self.pos.x, self.pos.y)
        for column in self.columns:
            self.set_column_content(cursor, column)
            cursor.x += self.pixel_case.x
            cursor.y = self.pos.y

    def draw(self, screen: pygame.Surface) -> None:
        for button in self.buttons:
            button.draw(screen)
        for text in self.texts:
            text.draw(screen)

    def get_press_button(self):
        '''
        get the first press button of the current frame
        '''
        for button in self.buttons:
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                return button
            


class SceneModal(SceneTime):
    '''
    scene with one text and one button
    '''

    def __init__(self, screen: pygame.Surface, view: 'View', texts: list,
            next_scene: str) -> None:
        super().__init__(screen, view)
        self.size_text = 30
        cx, cy = screen.get_size()
        self.texts = list()
        if isinstance(texts, str):
            self.texts.append(texts)
        else:
            self.texts = texts
        self.button = Button(self.screen, cx / 2 - 3 * cx / 12 /2 , 
            10 * cy / 12, 3 * cx / 12, 1 * cy / 12, img='confirm')
        self.next_scene = next_scene
        self.tables = list()
        self.set_table()
    
    def set_text(self):
           pass 

    def set_table(self):
        cx, cy = self.screen.get_size()
        x = 1 * cx / 12
        y = 1 * cy / 12
        w = 11 * cx / 12
        h = 8 * cy / 12
        self.tables.clear()
        string_per_col = list()
        string_per_col.append(self.texts)
        self.tables.append(Table(x, y, w, h, string_per_col))

    def update(self):
        super().update()
        self.do_press_button()

    def draw(self):
        super().draw()
        for table in self.tables:
            table.draw(self.screen)
        self.button.draw(self.screen)
    
    def do_press_button(self):
        if (self.view.mouse.release('left') and 
                self.button.rect.collidepoint(pygame.mouse.get_pos())):
            self.reset_entry_time()
            if self.next_scene == 'new_user_valid':
                self.view.end_new_user()
            else:
                self.view.current_scene = self.next_scene


class SceneModalCancelButton(SceneModal):
    def __init__(self, screen: pygame.Surface, view: 'View', texts: list,
            next_scene: str):
        super().__init__(screen, view, texts, next_scene)
        self.buttons = list()
        self.buttons.append(self.button)
        cx, cy = screen.get_size()
        self.buttons.append(Button(self.screen, cx/12 - 1 * cx / 12 / 2,
            10 * cy / 12, 1 * cx / 12, 1 * cy / 12, img='cancel'))

    def do_press_button(self):
        # valid button
        if (self.buttons[0].rect.collidepoint(pygame.mouse.get_pos()) and
                    self.view.mouse.release('left')):
            self.reset_entry_time()
            if self.next_scene == 'new_user_valid':
                self.view.end_new_user()
            else:
                self.view.current_scene = self.next_scene
        # cancel button
        if (self.buttons[1].rect.collidepoint(pygame.mouse.get_pos()) and
                    self.view.mouse.release('left')):
            self.reset_entry_time()
            self.view.cancel()

    def draw(self):
        for table in self.tables:
            table.draw(self.screen)
        for button in self.buttons:
            button.draw(self.screen)




class SceneKeyboard(SceneTime):
    '''
    scene with keyboard and two buttons
    '''

    def __init__(self, screen: pygame.Surface, view: 'View') -> None:
        super().__init__(screen, view)
        self.layout = self.layout_CH()
        cx, cy = screen.get_size()

        self.buttons = list()
        self.buttons.append(
            Button(self.screen, 1 * cx / 12, 0.2 * cy / 12, 1 * cx / 12,
                   1 * cy / 12))
        self.buttons.append(
            Button(self.screen, 10 * cx / 12, 0.2 * cy / 12, 1 * cx / 12,
                   1 * cy / 12, img='confirm'))
        self.load_keyboard()
        self.count = 0 
        self.input_text = ''
    
    def load_keyboard(self):
        self.keyboard = vkboard.VKeyboard(self.screen, self.on_key_event,
            self.layout, renderer=vkboard.VKeyboardRenderer.DARK, 
            special_char_layout=self.layout_special(),
            show_text=True)


    def on_key_event(self, text: str) -> None:
        print('Current text:', text)
        self.input_text = text
        self.reset_entry_time()

    def do_press_button(self):
        if (self.buttons[0].rect.collidepoint(pygame.mouse.get_pos()) and
                self.view.mouse.release('left')):
            self.count = 0
            self.view.cancel()
        if (self.buttons[1].rect.collidepoint(pygame.mouse.get_pos()) and
                self.view.mouse.release('left')):
            if  self.count == 0:
                self.count += 1
                self.view.do_unknown_badge(self.count)
                View.pipe['surname'] = self.keyboard.get_text()
                self.keyboard.set_text('')     
            elif self.count == 1:
                self.count += 1
                self.view.do_unknown_badge(self.count)
                View.pipe['name'] = self.keyboard.get_text()
                self.keyboard.set_text('')     


    def update(self):
        # print('view.SceneKeyboard.update', file=sys.stderr)
        super().update()
        events = self.view.events
        if Mouse().only_mouse:
            filtered_events = list(filter(lambda event: event.type in (
                Mouse().button['down'] | Mouse().button['up']), events))
        else:
            filtered_events = events
        #print('filtered_events : ', filtered_events, file=sys.stderr)
       #  if self.view.events.type in (Mouse.button['down'] |
       #                               Mouse.button['up']):
        # self.keyboard.update(self.view.events)
        self.keyboard.update(filtered_events)
        self.do_press_button()

    def draw(self):
        super().draw()
        self.keyboard.draw(self.screen, force=True)
        for button in self.buttons:
            button.draw(self.screen)
        
    @staticmethod
    def layout_CH() -> vkboard.VKeyboardLayout:
        model = [
            'qwertzuiop',
            'asdfghjkl',
            'yxcvbnm'
        ]
        return vkboard.VKeyboardLayout(model, height_ratio=9/12)

    @staticmethod
    def layout_special() -> vkboard.VKeyboardLayout:
        model = [
            '-áàâæãåäąç',
            'ĉćčďéèêëęě',
            'ĝğîĥïíìįĵł',
            'ñńöôœðûüùÿ'
        ]
        return vkboard.VKeyboardLayout(model, height_ratio=9/12)


class Mouse:
    '''
    unify MOUSEBUTTONDOWN and FINGERDOWN
    '''
    only_mouse = True
    button = dict()
    if only_mouse:
        button['down'] = set([pygame.MOUSEBUTTONDOWN])
        button['up'] = set([pygame.MOUSEBUTTONUP])
    else:
        button['down'] = set([pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN])
        button['up'] = set([pygame.MOUSEBUTTONUP, pygame.FINGERUP])
    def __init__(self) -> None:
        self.left = False
        self.old_left = False


    def update(self, events):
        self.old_left = self.left
        for event in events:
           # if (pygame.MOUSEBUTTONDOWN == event.type) or (pygame.FINGERDOWN == 
           # event.type):
            if  event.type in self.button['down']:
                self.left = True
            # elif (pygame.MOUSEBUTTONUP == event.type) or (pygame.FINGERUP == 
            # event.type):
            elif event.type in self.button['up']:
                self.left = False
        
    def release(self, button: str):
        '''
        detect release click
        up click
        
        '''
        return (not getattr(self, button)) and (getattr(self, f"old_{button}"))


class View:
    '''
    contain scene, pygame proprety,…
    '''
    debug = True

    # to communicate with other thread
    pipe = dict()

    def __init__(self, pipe: dict=None) -> None:
        self.running = True

        self._scenes = dict()
        self._current_scene = "wait"
        if pipe != None:
            View.pipe = pipe

    def load_pygame(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        # run that only on Raspberry Pi
        if os.name != "nt":
            self.screen = pygame.display.set_mode(
                (800, 480), pygame.FULLSCREEN)
            pygame.mouse.set_visible(False)
            pygame.display.set_allow_screensaver(True)
        else:
            self.screen = pygame.display.set_mode((800, 480))
        pygame.display.set_caption("Timbreuse")
        self.events = pygame.event.get()
        self.mouse = Mouse()
        self.background_color = pygame.Color('#ffffff')

    def load(self) -> None:
        '''
        start pygame loop
        '''
        self.load_pygame()
        self.load_scene()
        while self.running:
            if View.debug:
                #print("loop", file=sys.stderr)
                pass
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.running = False
                    
            self.update()
            self.draw()
        pygame.quit()
        self.__del__()

    def load_scene(self) -> None:
        self.scenes["wait"] = SceneWait(self.screen, self)
        self.reload_scene()

    def reload_scene(self) -> None:
        self.scenes["select"] = SceneSelect(self.screen, self)
        self.scenes["log"] = SceneLog(self.screen, self)
        self.scenes["time"] = SceneWorkTime(self.screen, self)
        self.scenes["last_time"] = SceneWorkTime(self.screen, self,
            'last_week')
        self.scenes["keyboard"] = SceneKeyboard(self.screen, self)


    def __del__(self) -> None:
        if View.debug:
            print('View.del, self pipe', self.pipe, file=sys.stderr)
        self.pipe['th_condition'].acquire()
        self.pipe['quit'] = True
        self.pipe['th_condition'].notify_all()
        self.pipe['th_condition'].release()
        pygame.quit()
        sys.exit()

    def update(self) -> None:
        '''
        is called each frame
        '''
        self.clock.tick(60)
        self.mouse.update(self.events)
        self.scenes[self.current_scene].update()
        if View.debug:
            self.debug_command()

    def debug_command(self):
        '''
        command to debug
        force change scene
        '''
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.running = False

        if pygame.key.get_pressed()[pygame.K_j]:
            # change scene ;  debug

            self.do_select_scene()

        if pygame.key.get_pressed()[pygame.K_k]:
            # change scene ;  debug

            self.do_log_scene(View.pipe['log'])

        if pygame.key.get_pressed()[pygame.K_l]:
            # change scene ;  debug
            self.do_unknown_badge()

    def draw(self) -> None:
        '''
        is called each frame. containt fonction to show
        '''
        self.screen.fill(self.background_color)
        self.scenes[self.current_scene].draw()
        pygame.display.flip()

    @property
    def current_scene(self) -> Scene:
        return self._current_scene

    @current_scene.setter
    def current_scene(self, newScene: str) -> None:
        print('current_scene.setter', self._current_scene, newScene,
              file=sys.stderr)

        if newScene in self.scenes.keys():
            self._current_scene = newScene
            if isinstance(self.scenes[newScene], SceneTime):
                self.scenes[newScene].reset_entry_time()
        else:
            print(self.scenes.keys(), file=sys.stderr)
            raise ValueError(f"scene {newScene} does not exist")
    
    @property
    def scenes(self) -> dict:
        return self._scenes
    
    @scenes.setter
    def scenes(self, tup: tuple) -> None:
        key = tup[0] # str
        new_scene = tup[1] # Scene
        print('View.scenes.setter', file=sys.stderr)
        if isinstance(key, str) and isinstance(new_scene, Scene):
            self._scenes[key] = new_scene
        else:
            raise TypeError(f'key must be a str and new_scene a Scene')

    def do_select_scene(self) -> None:
        '''
        change the current scene
        '''

        print("do_next_scene", file=sys.stderr)
        if self.current_scene != "select":
            self.current_scene = "select"
        else:
            self.current_scene = "wait"

    def do_wait_scene(self):
        self.current_scene = 'wait'

    def do_select_scene_dict(self, pipe: dict):
        '''
        change the current scene and change the reference of View.pipe
        '''
        print("do_next_scene_dict", file=sys.stderr)
        View.pipe = pipe
        self.do_select_scene()

    def do_log_scene(self, log) -> None:
        if self.current_scene == 'select':
            self.current_scene = 'log'
            self.scenes['log'].set_texts(log)

    def do_work_time(self, time='time') -> None:
        if ((self.current_scene == 'log' and time == 'time') or
            (self.current_scene == 'time' and time == 'last_time')):

            self.current_scene = time
            self.scenes[time].set_content()

    def do_unknown_badge_dict(self, pipe: dict):
        View.pipe = pipe
        self.scenes['keyboard'].count = 0
        self.do_unknown_badge()

    @classmethod
    def read_pipe(cls, pipe: dict):
        View.pipe = pipe
        

    def do_unknown_badge(self, count: int=0):
        texts = list()
        if count == 0:
            texts.append("Le badge est inconnu.")
            texts.append("Veuillez taper votre nom de famille.")
            next_scene = 'keyboard'
        elif count == 1:
            texts.append("Veuillez taper votre prénom.")
            next_scene = 'keyboard'
        else:
            texts.append('Veuillez rescanner votre badge après validation')
            texts.append('de ce message.')
            next_scene = 'new_user_valid'

        # setter is use
        if count == 0:
            self.scenes = 'modal', SceneModalCancelButton(self.screen, self,
                    texts, next_scene)
        else:
            self.scenes = 'modal', SceneModal(self.screen, self, texts,
                    next_scene)
        self.current_scene = 'modal'

    def cancel(self):
        '''
        when time expire or press quit button
        '''
        self.current_scene = 'wait'
        self.reload_scene()
        View.pipe['cancel'] = True
        View.pipe['th_condition'].acquire()
        View.pipe['th_condition'].notify_all()
        View.pipe['th_condition'].release()


    def end_new_user(self):
        '''
        reset for end of new user
        '''
        self.current_scene = 'wait'
        self.reload_scene()
        View.pipe['new_user_valid'] = True
        View.pipe['th_condition'].acquire()
        View.pipe['th_condition'].notify_all()
        View.pipe['th_condition'].release()


class Text:
    def __init__(self, x: float, y: float, size: float, text: str,
            color: pygame.Color=pygame.Color('#212529'),
            align: str='left') -> None:
        '''
        text with position, size and color
        '''
        self.__text = text
        self.pos = pygame.math.Vector2(x, y)
        self.size = size
        self.font = Loader.load_txt('liberation', self.size)
        self.color = color
        self.img = self.font.render(self.text, True, self.color)
        self.align = align
        self.set_align()

    @property
    def strikethrough(self):
        return self.font.strikethrough

    @strikethrough.setter
    def strikethrough(self, is_active: bool):
        '''
        20230124 striketrough is not yet in the stable version of pygame but
        it is in a doc of pygame, if error do italic and underline
        '''
        try:
            self.font.strikethrough = is_active
            self.update()
        except:
            self.color = pygame.Color("#6c767e")
            self.italic = is_active


    @property
    def italic(self):
        return self.font.italic

    @italic.setter
    def italic(self, is_active: bool):
        self.font.italic = is_active
        self.update()
    
    @property
    def underline(self):
        return self.font.underline

    @underline.setter
    def underline(self, is_active: bool):
        self.font.underline = is_active
        self.update()

    @property
    def bold(self):
        return self.font.bold

    @bold.setter
    def bold(self, is_active: bool):
        self.font.bold = is_active
        self.update()

    def set_align(self) -> None:
        if self.align == 'center':
            self.pos.x -= self.img.get_width() / 2

    def update(self) -> None:
        '''
        is called each frame
        '''
        self.img = self.font.render(self.text, True, self.color)

    def draw(self, screen: pygame.Surface) -> None:
        '''
        is called each frame. containt function to show
        '''
        screen.blit(self.img, self.pos)

    def __str__(self) -> str:
        return self.text

    @property
    def text(self) -> str:
        return self.__text

    @text.setter
    def text(self, txt: str):
        if isinstance(txt, str):
            self.__text = txt
        else:
            raise ValueError("must be str")

    def __call__(self, text: str):
        self.text = text
        self.update()
    
    
class Loader:
    '''
    load file 
    '''
    paths = dict()
    paths['cancel'] = 'icons/x.bmp'
    paths['liberation'] = 'fonts/LiberationSans-Regular.ttf'
    paths['in'] = 'icons/box-arrow-in-right.bmp'
    paths['out'] = 'icons/box-arrow-right.bmp'
    paths['log'] = 'icons/clock-history.bmp'
    paths['return'] = 'icons/arrow-left.bmp'
    paths['more'] = 'icons/three-dots.bmp'
    paths['confirm'] = 'icons/check.bmp'
    paths['detail'] = 'icons/zoom-in.bmp'
    paths['next'] = 'icons/arrow-right.bmp'
    paths['logo'] = 'img/logo_orif_small_transparent.bmp'
    

    @classmethod
    def load_icon(cls, name: str, color: pygame.Color=None):
        print('Loader.load', file=sys.stderr)
        if color is None:
            return pygame.image.load(cls.paths[name])
        else:
            
            return cls.change_color(pygame.image.load(cls.paths[name]), color)

    @classmethod
    def load_img(cls, name: str):
        return pygame.image.load(cls.paths[name])
    
    @classmethod
    def load_txt(cls, name: str, size: int) -> pygame.font.Font:
        print('load_txt', file=sys.stderr)
        try:
            return pygame.font.Font(cls.paths[name], size)
        except TypeError:
            return pygame.font.Font(cls.paths[name], int(size))

    
    @staticmethod
    def change_color(img: pygame.Surface,
            color: pygame.Color) -> pygame.Surface:
        w, h = img.get_size()
        r, g, b, _ = color
        for x, y in product(range(w), range(h)):
           alpha = img.get_at((x,y))[3]
           img.set_at((x, y), pygame.Color(r, g, b, alpha))
        return img


def test1():
    # test value
    pipe = dict()
    pipe['name'] = 'Bob'
    pipe['surname'] = 'Leta'
    pipe['log'] = list()
    pipe['log'].append(dict())
    pipe['log'].append(dict())
    pipe['log'][0]['date'] = datetime.datetime(2022, 2, 18, 15, 28, 49)
    pipe['log'][1]['date'] = datetime.datetime(2022, 1, 19, 16, 30, 51)
    pipe['log'][0]['inside'] = True
    pipe['log'][1]['inside'] = False
    pipe['time_last_week'] = datetime.timedelta(seconds=144243)
    pipe['time_current_week'] = datetime.timedelta(seconds=144243)
    pipe['day_current_week'] = ((datetime.date(2022, 4, 29), 
        datetime.timedelta(seconds=28872)), (datetime.date(2022, 4, 28), 
        datetime.timedelta(seconds=28843)), (datetime.date(2022, 4, 27),
        datetime.timedelta(seconds=28843)), (datetime.date(2022, 4, 26),
        datetime.timedelta(seconds=28843)), (datetime.date(2022, 4, 25),
        datetime.timedelta(seconds=28843)))
    pipe['day_last_week'] = ((datetime.date(2022, 4, 22), 
        datetime.timedelta(seconds=28871)), (datetime.date(2022, 4, 21), 
        datetime.timedelta(seconds=28843)), (datetime.date(2022, 4, 20),
        datetime.timedelta(seconds=28843)), (datetime.date(2022, 4, 19),
        datetime.timedelta(seconds=28843)), (datetime.date(2022, 4, 18),
        datetime.timedelta(seconds=28843)))
    pipe['current_week'] = ([(datetime.datetime(2022, 4, 29, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 29, 15, 38, 54), 0),
        (datetime.datetime(2022, 4, 29, 15, 38, 43), 1),
        (datetime.datetime(2022, 4, 29, 8, 8, 51), 1)],
        [(datetime.datetime(2022, 4, 28, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 28, 15, 53, 23), 0),
        (datetime.datetime(2022, 4, 28, 15, 53, 19), 1),
        (datetime.datetime(2022, 4, 28, 8, 8, 51), 1)],
        [(datetime.datetime(2022, 4, 27, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 27, 8, 8, 51), 1)],
        [(datetime.datetime(2022, 4, 26, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 26, 8, 8, 51), 1)],
        [(datetime.datetime(2022, 4, 25, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 25, 15, 38, 54), 0),
        (datetime.datetime(2022, 4, 25, 15, 38, 43), 1),
        (datetime.datetime(2022, 4, 25, 8, 8, 51), 1)])

    pipe['last_week'] = ([(datetime.datetime(2022, 4, 22, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 22, 15, 38, 54), 0),
        (datetime.datetime(2022, 4, 22, 15, 38, 43), 1),
        (datetime.datetime(2022, 4, 22, 8, 8, 51), 1)],
        [(datetime.datetime(2022, 4, 21, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 21, 15, 53, 23), 0),
        (datetime.datetime(2022, 4, 21, 15, 53, 19), 1),
        (datetime.datetime(2022, 4, 21, 8, 8, 51), 1)],
        [(datetime.datetime(2022, 4, 20, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 20, 8, 8, 51), 1)],
        [(datetime.datetime(2022, 4, 19, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 19, 8, 8, 51), 1)],
        [(datetime.datetime(2022, 4, 18, 16, 9, 34), 0),
        (datetime.datetime(2022, 4, 18, 15, 38, 54), 0),
        (datetime.datetime(2022, 4, 18, 15, 38, 43), 1),
        (datetime.datetime(2022, 4, 18, 8, 8, 51), 1)])
    view = View(pipe)
    view.load()


def main():
    view = View()
    view.load()

def doctest():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    mode = 2
    if mode == 0:
        main()
    elif mode == 1:
        test1()
    elif mode == 2:
        doctest()
