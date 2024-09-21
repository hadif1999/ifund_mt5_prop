from pydantic import BaseModel

class Mt5User(BaseModel):
    first_name: str
    second_name: str
    pre_phone: str = "+98"
    broker: str = "Amarkets-Demo"
    balance: int = 1000
    phone: str | None = None
    email: str | None = None
    account_type: str = "demo"


class User(BaseModel):
    username: str
    password: str
    broker_userdata: Mt5User
    
    
    
class UserExpertData(BaseModel):
    Name: str|None 
    Type: str = "Standard MT5 USD"
    Server: str|None 
    Login: int | str | None 
    Password: str|None 
    Investor: str|None 
    initial_balance: int|None 
    auto_trade_check_period: int|None 
    gain_send_time_gmt: int|None 
    max_total_dd: float|None 
    max_daily_dd: float|None 
    min_position_duration_seconds: int|None 
    max_position_with_min_duration: int|None 
    api_sandbox_mode: bool|None 
    position_under_min: int | None 
    total_position_under_min: int | None 
    reset: bool|None 
    
    
class ChangePassword(BaseModel):
    old: str
    new: str 
    broker: str
