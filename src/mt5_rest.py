from httpx import AsyncClient, Response


class MT5Rest:
    NEW_ACCOUNT = "/GetDemo"
    CHANGE_PASSWORD = "/ChangePassword"
    CONNECT = "/Connect"
    PORT = 80
    HOST = "127.0.0.1"
    IMAGE_NAME = "hadi1999/meta5rest:latest"
        
    
    @staticmethod
    async def _aget(_url:str, **kwargs) -> Response:
        async with AsyncClient() as client:
            res = await client.get(_url, **kwargs)
        return res
    
    
    @staticmethod
    async def _apost(_url: str, **kwargs) -> Response:
        async with AsyncClient() as client:
            res = await client.post(_url, **kwargs)
        return res
    
    def __init__(self) -> None:
        self.__token = None
    
    
    async def connect(self, login: str, password: str, 
                      dns: str = "78.140.180.198", dns_port=443):
        url = __class__.get_url(__class__.CONNECT)
        res = await __class__._aget(url, params = {"user": login, "password": password,
                                                   "host": dns, "port": dns_port})
        self.__token = res.text.strip()
        return self.__token
    
    
    @staticmethod
    async def create_new_account(*, broker: str = "alpari", 
                                 username:str = "firstname secondname", 
                                 country: str = "canada", city="Toronto", state="Toronto", 
                                 zipcode:int = 12345, address:str = "any test address", 
                                 phone:str = "+12405887433", email:str = "testmail@email.com", 
                                 deposit: int = 1000000, leverage:int = 100,
                                 dns: str = "78.140.180.198", dns_port: int = 443):
        url = __class__.get_url(__class__.NEW_ACCOUNT)
        _params = {"host": dns, "port": dns_port, "userName": username,
                   "accType": "demo", "country": country, "city": city,
                   "state": state, "zipCode": zipcode, "address": address, 
                   "phone": phone, "email": email, "companyName": broker,
                   "deposit": deposit, "leverage": leverage}
        res = await __class__._aget(url, params = _params)
        return res.json()
    
    
    async def change_account_password(self, new_pass:str):
        if self.__token: 
            id = self.__token
            url = self.get_url(__class__.CHANGE_PASSWORD)
            res = await self._aget(url, params={"id": id, "password": new_pass})
            return res.text.strip().upper()

    
    def BaseURL():
        return f"{__class__.HOST}:{__class__.PORT}"
    
    
    def get_url(path:str):
        return __class__.BaseURL() + path 
    
    