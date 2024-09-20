
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver import ActionChains
from selenium.common.exceptions import MoveTargetOutOfBoundsException

def search_url(url:str, driver_obj: webdriver.Chrome, delay:int = 5):
    driver_obj.get(url)
    time.sleep(delay)



def login_account(driver_obj: webdriver.Chrome, delay_between_actions:float = 0.5):
    item_number = 14
    ActionChains(driver_obj).send_keys(Keys.ALT).perform() # opens File menu
    time.sleep(delay_between_actions)
    ActionChains(driver_obj).send_keys(Keys.DOWN*item_number).perform() # goes to login button
    time.sleep(delay_between_actions)
    ActionChains(driver_obj).send_keys(Keys.ENTER*2).perform() # logins with predefined properties
    return True


def add_broker(driver_obj: webdriver.Chrome, delay_between_actions: float = 0.5, 
                broker:str = "amarkets"):
    item_number = 11
    action = ActionChains(driver_obj).send_keys(Keys.ALT).perform() # opens File menu
    time.sleep(delay_between_actions) 
    ActionChains(driver_obj).send_keys(Keys.DOWN * item_number).perform() # goes to open account button
    time.sleep(delay_between_actions) 
    action = ActionChains(driver_obj).send_keys(Keys.ENTER*2) # enter select broker page
    action.key_down(Keys.SHIFT).send_keys(Keys.TAB*2).key_up(Keys.SHIFT).perform()
    time.sleep(delay_between_actions)
    ActionChains(driver_obj).send_keys(broker).send_keys(Keys.ENTER).perform() # searches for broker
    time.sleep(delay_between_actions+1) 
    ActionChains(driver_obj).send_keys(Keys.TAB).send_keys(Keys.ENTER)
    time.sleep(delay_between_actions) 
     # go to select account type page
    ActionChains(driver_obj).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
    time.sleep(delay_between_actions)
    ActionChains(driver_obj).send_keys(Keys.TAB*2).send_keys(Keys.ENTER).perform()
    time.sleep(delay_between_actions)
    return True


def create_new_user(drver_obj:webdriver.Chrome, 
                    user_data:dict[str, str] = {"first_name":"Hamed",
                                                "second_name":"zovei",
                                                "email":"test1@gmail.com",
                                                "phone":"9218000001",
                                                "pre_phone":"+98",
                                                "deposit":10000}, 
                    delay_between_actions:float = 0.2, type:str = "demo", 
                    broker_supports_leverage:bool = False):
    
    leverage_const = 2 if broker_supports_leverage else 1
    
    # filling open account form 
    #firstname
    # clear text field
    action = ActionChains(drver_obj)
    action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE)
    action.send_keys(user_data["first_name"]) 
    action.send_keys(Keys.TAB)
    action.perform()
    time.sleep(delay_between_actions)
    # second name
    action = ActionChains(drver_obj)
    action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE)
    action.send_keys(user_data["second_name"])
    action.send_keys(Keys.TAB)
    action.perform()
    time.sleep(delay_between_actions)
    # email
    action = ActionChains(drver_obj)
    action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE)
    action.send_keys(user_data["email"])
    action.send_keys(Keys.TAB)
    action.perform()
    time.sleep(delay_between_actions)
    # pre phone
    action = ActionChains(drver_obj)
    action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE)
    action.send_keys(user_data["pre_phone"])
    action.send_keys(Keys.TAB)
    action.perform()
    time.sleep(delay_between_actions)
    # phone 
    action = ActionChains(drver_obj)
    action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE)
    action.send_keys(user_data["phone"])
    action.send_keys(Keys.TAB *3)
    action.perform()
    time.sleep(delay_between_actions)
    # deposit 
    action = ActionChains(drver_obj)
    action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE)
    action.send_keys(user_data["deposit"])
    action.send_keys(Keys.TAB * leverage_const)
    action.send_keys(Keys.SPACE) # selecting 
    action.perform()
    time.sleep(delay_between_actions)
    # going to select accont type page
    action = ActionChains(drver_obj).send_keys(Keys.TAB * 2)
    # selecting demo
    if type == "demo": action.send_keys(Keys.ENTER)
    
    action.perform()
    time.sleep(delay_between_actions)
    return True


def current_datetime():
    import datetime as dt
    return dt.datetime.now().strftime("%d_%m_%Y_%H:%M:%S")


def read_from_clipboard() -> str:
    import pyperclip
    # clipboard.copy("abc")  # now the clipboard content will be string "abc"
    text = pyperclip.paste()
    return text


def empty_clipboard():
    import pyperclip
    pyperclip.copy('') # clearing clipboard
    


def image2txt(image_dir:str):
    import pytesseract
    from PIL import Image
    # Open the image file
    image = Image.open(image_dir)
    image = image.crop((500, 200, 1000, 800))
    image.size
    # Perform OCR using PyTesseract
    text = pytesseract.image_to_string(image, "eng")
    return text


def extract_userdata(raw_data:str):
    data_list = raw_data.split('\n')
    user_data = {}
    for data in data_list:
        if data in ['', " ", "  "]: continue
        data_key, data_val = data.split(':')
        user_data[data_key.strip()] = data_val.strip()
    return user_data



def init(driver_obj: webdriver.Chrome, delay:int = 15, window_size: dict = {"width": 1409, 
                                                                            "height": 696}, 
         window_position: dict = {'x': 2, 'y': 70}):
    
    print("\ninitializing driver ...")
    driver_obj.maximize_window()
    driver_obj.set_window_size(**window_size)
    driver_obj.set_window_position(**window_position)
    ActionChains(driver_obj).send_keys(Keys.ESCAPE).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
    time.sleep(delay)
    ActionChains(driver_obj).send_keys(Keys.ESCAPE).perform()
    time.sleep(delay//10)
    driver_obj.set_window_size(**window_size)
    driver_obj.set_window_position(**window_position)
    
    
def open_options_menu(driver_obj: webdriver.Chrome, delay=0.5):
    action = ActionChains(driver_obj).send_keys(Keys.ALT).send_keys(Keys.RIGHT * 4)
    # open options menu
    action.send_keys(Keys.UP).send_keys(Keys.ENTER).perform()
    time.sleep(delay)
    
    
def change_account_password(driver_obj: webdriver.Chrome,
                            old:str, new:str,
                            delay:int = 0.5):
    open_options_menu(driver_obj)
    # selecting tabs
    ActionChains(driver_obj).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
    time.sleep(delay)
    # go to change password page
    ActionChains(driver_obj).send_keys(Keys.LEFT * 3).send_keys(Keys.TAB * 4).perform()
    time.sleep(delay)
    # changing password
    ## enter old pass
    ActionChains(driver_obj).send_keys(old).perform()
    time.sleep(delay)
    # enter new pass
    ActionChains(driver_obj).send_keys(Keys.TAB * 2).send_keys(new).perform()
    time.sleep(delay)
    # repeat new pass
    ActionChains(driver_obj).send_keys(Keys.TAB).send_keys(new).perform()
    # press ok
    ActionChains(driver_obj).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
    time.sleep(delay)
    ActionChains(driver_obj).send_keys(Keys.ESCAPE * 2).perform()
    return True


def ctrlc(driver_obj: webdriver.Chrome):
    ActionChains(driver_obj).key_down(Keys.LEFT_CONTROL).send_keys('c'). \
    key_up(Keys.LEFT_CONTROL).perform()
    

def read_userdata_by_selection(driver_obj: webdriver.Chrome, delay: float = 0.5,
                                 location_pct: tuple[float] = (0.35, 0.525)):
    print("\nreading user data...")
    # giving needed permissions
    driver_obj.set_permissions('clipboard-read', 'granted')
    driver_obj.set_permissions('clipboard-write', 'granted')
    time.sleep(delay)
    empty_clipboard()
    move_mouse_by_pct(driver_obj, *location_pct, delay = delay)
    ActionChains(driver_obj).double_click().perform()
    time.sleep(delay)
    # reading login id
    ctrlc(driver_obj); ctrlc(driver_obj);ctrlc(driver_obj)
    time.sleep(delay+1)    
    login = read_from_clipboard().strip()
    ActionChains(driver_obj).send_keys(Keys.TAB).perform()
    time.sleep(delay)
    # reading password
    ctrlc(driver_obj); ctrlc(driver_obj);ctrlc(driver_obj)
    time.sleep(delay)    
    password = read_from_clipboard().strip()
    ActionChains(driver_obj).send_keys(Keys.TAB).perform()
    time.sleep(delay)
    # reading investor
    ctrlc(driver_obj); ctrlc(driver_obj); ctrlc(driver_obj)
    time.sleep(delay)    
    investor = read_from_clipboard().strip()
    ActionChains(driver_obj).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform() 
    time.sleep(delay)        
    empty_clipboard()
    move_mouse_by_pct(driver_obj, *location_pct, delay=delay, reverse=True)
    return {"Login":login, 'Password':password, 'Investor':investor}


def read_userdata(driver_obj: webdriver.Chrome, delay = 1):
    # moving to another window and back
    empty_clipboard()
    action = ActionChains(driver_obj)
    action.key_down(Keys.ALT).key_down(Keys.CONTROL).send_keys(Keys.RIGHT).perform()
    time.sleep(delay)
    action = ActionChains(driver_obj)
    action.key_down(Keys.ALT).key_down(Keys.CONTROL).send_keys(Keys.LEFT).perform()
    ActionChains(driver_obj).key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
    time.sleep(delay)
    # reading login id
    ctrlc(driver_obj); ctrlc(driver_obj);ctrlc(driver_obj)
    time.sleep(delay+1)    
    login = read_from_clipboard().strip()
    ActionChains(driver_obj).send_keys(Keys.TAB).perform()
    time.sleep(delay)
    # reading password
    ctrlc(driver_obj); ctrlc(driver_obj);ctrlc(driver_obj)
    time.sleep(delay+1)    
    password = read_from_clipboard().strip()
    ActionChains(driver_obj).send_keys(Keys.TAB).perform()
    time.sleep(delay)
    # reading investor
    ctrlc(driver_obj); ctrlc(driver_obj); ctrlc(driver_obj)
    time.sleep(delay+1)    
    investor = read_from_clipboard().strip()
    ActionChains(driver_obj).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform() 
    time.sleep(delay)        
    empty_clipboard()
    return {"Login":login, 'Password':password, 'Investor':investor}  
    

def move_mouse_by_pct(driver_obj: webdriver.Chrome, x_pct:float, y_pct: float, delay = 1,
                      reverse: bool = False):
    location = location_from_pct(driver_obj, x_pct, y_pct)
    if reverse: location = tuple([-l for l in location])
    ActionChains(driver_obj).move_by_offset(*location).perform()
    time.sleep(delay)
    return True


def get_WidthHeight(driver_obj: webdriver.Chrome):
    canvas_width_script = """
    var iframe = document.getElementsByTagName('iframe')[0];
    var iframeDocument = iframe.contentDocument;
    return iframeDocument.getElementsByTagName('canvas')[0].width;
    """
    canvas_height_script = """
    var iframe = document.getElementsByTagName('iframe')[0];
    var iframeDocument = iframe.contentDocument;
    return iframeDocument.getElementsByTagName('canvas')[0].height;
    """
    width, height = (driver_obj.execute_script(canvas_width_script),
                    driver_obj.execute_script(canvas_height_script))
    return 1409, 696


def location_from_pct(driver_obj:webdriver.Chrome,
                      width_pct: float = 0.1, height_pct: float = 0.1):
    width, height = get_WidthHeight(driver_obj)
    return width * width_pct, height * height_pct


def autotrade(driver_obj: webdriver.Chrome, delay = 0.4, reset: bool = False):
    print("\nsetting autotrade...")
    action = ActionChains(driver_obj).key_down(Keys.CONTROL).send_keys('e').key_up(Keys.CONTROL)
    action.perform()
    time.sleep(delay)
    if not reset: return True
    action = ActionChains(driver_obj).key_down(Keys.CONTROL).send_keys('e').key_up(Keys.CONTROL)
    action.perform()
    time.sleep(delay)
    return True


def switch_toolbox_view(driver_obj: webdriver.Chrome, delay: float = 1):
    item_number = 10
    action = ActionChains(driver_obj)
    # go to views menu
    action.send_keys(Keys.ALT).send_keys(Keys.RIGHT)
    # go to toolbox button
    action.send_keys(Keys.DOWN * item_number)
    action.send_keys(Keys.ENTER).perform()
    time.sleep(delay)
    return True


def open_expert_advisors_menu(driver_obj: webdriver.Chrome, delay = 0.5):
    action = ActionChains(driver_obj)
    # go to insert tab
    action.send_keys(Keys.ALT).send_keys(Keys.RIGHT * 2)
    # opening experts menu
    action.send_keys(Keys.DOWN * 3).send_keys(Keys.RIGHT)
    action.perform()    
    time.sleep(delay)
    return True


def activate_iFund_expert(driver_obj: webdriver.Chrome, delay = 0.5):
    print("\nactivating Ifund expert...")
    open_expert_advisors_menu(driver_obj, delay)
    action = ActionChains(driver_obj)
    # activating iFund expert
    action.send_keys(Keys.DOWN * 5).send_keys(Keys.ENTER).send_keys(Keys.TAB)
    action.send_keys(Keys.ENTER).perform()
    time.sleep(delay)
    return True




with_leverage_brokers = ["alpari", "fxtm"]

class MT5_Manager:
    def __init__(self, url:str,
                 window_size: dict[str, int] = {"width": 1409, "height": 696},
                 window_position: dict[str, int] = {'x': 2, 'y': 70}) -> None:
        self.__auth_url = url
        self.window_size = window_size
        self.window_position = window_position
        
        
        #self.leverage_const = 2 if broker in with_leverage_brokers else 1
        
    def build_driver(self):
        from webdriver_manager.chrome import ChromeDriverManager
        from pyvirtualdisplay import Display
        
        w, h = self.window_size["width"], self.window_size["height"]
        x, y = self.window_position['x'], self.window_position['y']
        opts = webdriver.ChromeOptions()
        self.display = Display(visible=0, size=(w, h))  # Set resolution to 1920x1080
        self.display.start()
        opts.add_argument("--start-maximized")
        opts.add_argument(f"--window-size={w},{h}")
        opts.add_argument(f"--window-position={x},{y}")
        # opts.add_argument("--headless")
        # opts.add_argument("--kiosk")
        opts.add_argument("--no-sandbox")
        # opts.add_experimental_option("detach", True)
        service = webdriver.ChromeService(ChromeDriverManager().install()) 
        self.driver = webdriver.Chrome(opts, service)
        self.driver.get(self.__auth_url)
        
        
    def init(self, delay = 10):
        return init(self.driver, delay, self.window_size, self.window_position)
        
        
    def add_broker(self, delay: float=0.5, broker:str = "amarkets"):
        return add_broker(self.driver, delay, broker)
    
    
    def move_mouse_by_pct(self, x_pct, y_pct, reverse = False, delay=1):
        return move_mouse_by_pct(self.driver, x_pct, y_pct, delay, reverse)
    
    
    def create_new_account(self, user_data: dict[str, str] = { "first_name": "Hamed",
                                                              "second_name": "zovei",
                                                              "email": "test1@gmail.com",
                                                              "phone": "9218000001",
                                                              "pre_phone": "+98",
                                                              "deposit": 10000}, 
                           delay:float = 0.5, type:str = "demo", broker:str = "amarkets"):
        broker_supports_leverage = True if broker in with_leverage_brokers else False
        return create_new_user(self.driver, user_data, delay, type,broker_supports_leverage)
        
        
    def read_userdata(self, delay: float = 1, raise_empty: bool = True)-> dict[str]:
        empty_clipboard()
        self.user_data = read_userdata(self.driver, delay)
        if '' in self.user_data.values() and raise_empty: 
            raise ValueError("userdata is empty!")
        return self.user_data
    
    
    def login_account(self, delay: float = 0.5):
        return login_account(self.driver, delay)
    
    
    def autotrade(self, delay: float = 0.5, reset: bool = False):
        return autotrade(self.driver, delay, reset)
    
    
    def switch_toolbox_view(self, delay: float = 1):
        return switch_toolbox_view(self.driver, delay)
    
    
    def open_expert_advisors_menu(self, delay: float = 0.5):
        return open_expert_advisors_menu(self.driver, delay)
    
    
    def activate_IFund_expert(self, delay: float = 0.5):
        return activate_iFund_expert(self.driver, delay)
    
    
    def change_account_password(self, old:str, new:str, delay=0.5):
        return change_account_password(self.driver, old, new, delay)
    
    
    def exit_update(self, delay = 0.5):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).send_keys(Keys.TAB) \
        .send_keys(Keys.ENTER).perform()
        time.sleep(delay)
    
    
    def quit(self, delay: float = 1):
        time.sleep(delay)
        self.driver.quit()
        self.display.stop()
        return True
    
    
    
    
        
    
        
    
        
    
