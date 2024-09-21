from httpx import AsyncClient, Response, AsyncHTTPTransport, Timeout




class MT5Rest:
    ## endpoints
    NEW_ACCOUNT = "/GetDemo"
    CHANGE_PASSWORD = "/ChangePassword"
    CONNECT = "/Connect"
    PING = "/Ping"
    PING_HOST = "/PingHost"
    SEARCH_BROKER_IPS = "/Search"
    ####
    PORT = 8000
    HOST = "127.0.0.1"
    IMAGE_NAME = "hadi1999/meta5rest:latest"
    _transport = AsyncHTTPTransport(retries=5)
    _timeout = Timeout(10, connect=15, read=10)
        
    
    @staticmethod
    async def _aget(_endpoint:str, **kwargs) -> Response:
        async with AsyncClient(transport=__class__._transport, 
                               timeout=__class__._timeout, http2=True,
                               base_url=__class__.BaseURL()) as client:
            res = await client.get(_endpoint, **kwargs)
        return res
    
    
    @staticmethod
    async def _apost(_endpoint: str, **kwargs) -> Response:
        async with AsyncClient(transport=__class__._transport,
                               timeout=__class__._timeout, http2=True,
                               base_url=__class__.BaseURL()) as client:
            res = await client.post(_endpoint, **kwargs)
        return res
    
    
    def __init__(self) -> None:
        self.__token = None

    
    async def connect(self, login: str, password: str, 
                      dns: str = "78.140.180.198", dns_port=443):
        res = await __class__._aget(__class__.CONNECT, params = {"user": login,
                                                                 "password": password,
                                                                 "host": dns,
                                                                 "port": dns_port})
        self.__token = res.text.strip()
        assert len(self.__token) > 1, "something wrong with evaluated token"
        return self.__token
    
    
    @staticmethod
    async def create_new_account(*, broker: str = "alpari", 
                                 username:str = "firstname secondname", 
                                 country: str = "canada", city="Toronto", state="Toronto", 
                                 zipcode:int = 12345, address:str = "any test address", 
                                 phone:str = "+12405887433", email:str = "testmail@email.com", 
                                 deposit: int = 1000000, leverage:int = 100,
                                 dns: str = "78.140.180.198", dns_port: int = 443):
        _params = {"host": dns, "port": dns_port, "userName": username,
                   "accType": "demo", "country": country, "city": city,
                   "state": state, "zipCode": zipcode, "address": address, 
                   "phone": phone, "email": email, "companyName": broker,
                   "deposit": deposit, "leverage": leverage}
        res = await __class__._aget(__class__.NEW_ACCOUNT, params = _params)
        res = res.json()
        assert "login" in res and "password" in res, "no login and password fields found in response"
        return res
        
    
    async def change_account_password(self, new_pass:str):
        if self.__token: 
            id = self.__token
            res = await self._aget(__class__.CHANGE_PASSWORD, params={"id": id, 
                                                                      "password": new_pass})
            res = res.text.strip().upper()
            assert "OK" in res, "something went wrong when changing password"
            return res
        else: 
            ValueError("not connected yet")


    @staticmethod
    async def find_broker_ips(broker: str):
        res = await __class__._aget(__class__.SEARCH_BROKER_IPS, params={"company":broker})
        dns_ls = res.json()["results"]
        dns_name_ls = [dns["name"] for dns in dns_ls]
        if broker not in dns_name_ls: 
            raise ValueError(f"broker name {broker} not found in {dns_name_ls")
        ip_ls: list[str] = [dns["access"] for dns in dns_ls
                            if broker.lower() == dns["name"].lower()][0]
        ip_ls_ping = [{"ip": (ip_sep := ip.split(':'))[0], 
                       "port": ip_sep[1], 
                       "ping": await __class__.ping_host(ip_sep[0], ip_sep[1])}
                       async for ip in ip_ls]
        ip_ls_ping_sort = sorted(ip_ls_ping, key=lambda x: x["ping"])    
        return ip_ls_ping_sort
    
    
    @staticmethod
    async def get_broker_ServerNames(broker: str):
        res = await __class__._aget(__class__.SEARCH_BROKER_IPS, params={"company":broker})
        dns_ls = res.json()["results"]
        return [dns["name"] for dns in dns_ls]
        

    @staticmethod
    async def ping_host(ip: str, port: int = 443):
        res = await __class__._aget(__class__.PING_HOST, params={"host":ip,
                                                                 "port":port})
        ping_time = int(res.text.strip())
        return ping_time
    

    @staticmethod
    async def ping():
        res = await __class__._aget(__class__.PING)
        res = res.text.strip().upper()
        assert "OK" in res, "problem with connection !"
        return res
            
    
    def BaseURL():
        return f"http://{__class__.HOST}:{__class__.PORT}"
    
    
    @staticmethod
    def get_url(path:str):
        return __class__.BaseURL() + path 
    
    
