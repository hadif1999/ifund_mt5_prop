import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
import uvicorn
import os
import asyncio
import docker
from docker import errors as DockerErrors
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
import random
import json
from typing import Annotated
from contextlib import asynccontextmanager
from docker.models.containers import Container
from loguru import logger
from src.schemas import User, UserExpertData, ChangePassword
from src.mt5_rest import MT5Rest
from src.docker_utils import (client, build_image, current_image_name_list,
                              get_allocated_ports, get_active_container_ids,
                              get_container_userpass_from_id, get_image_name_from_container, 
                              get_active_container_ports, image_exists, mt5_image_name, 
                              create_mt5_rest_container, clear_docker_env, remove_mt5rest)


@asynccontextmanager
async def lifespan(app: FastAPI):
    image_names = [mt5_image_name, MT5Rest.IMAGE_NAME]
    ###### removing mt5rest container if found
    remove_mt5rest()
    #### clean env 
    clear_docker_env()
    ####### pulling needed images
    for image_name in image_names: # pulling needed images
        if not image_exists(image_name):
                build_image(image_name)
    ####### 
    yield
    remove_mt5rest()
    clear_docker_env()


app = FastAPI(lifespan=lifespan)
users_data_dir = "./data/users/"  # keep using / at end
HOST_IP = "51.89.168.20"


def generate_random_port(start: int = 4000, end: int = 7000, image_name:str = mt5_image_name):
    unique = False
    while not unique:
        port = random.randint(start, end)
        unique = port not in get_allocated_ports(image_name=image_name)
    return port


def read_json_template(directory: str = '.', name: str = "ifund-config.json"):
    with open(f"{directory}/{name}", "r") as file:
        conf_dict = json.loads(file.read())
    return conf_dict


def save_user_json_data(json_data: dict, username: str) -> str:
    """saves json file and returns it's rel path

    Args:
        json_data (dict)
        username (str)

    Returns:
        str: json file path
    """
    global users_data_dir
    json_folder_dir = os.path.abspath(users_data_dir + username)
    json_file_name = json_folder_dir + f"/ifund-config.json"
    os.makedirs(json_folder_dir, exist_ok=True)
    with open(json_file_name, "w") as file:
        file.write(json.dumps(json_data))
    return json_folder_dir


def read_user_json_data(username: str) -> dict:
    global users_data_dir
    json_folder_dir = os.path.abspath(users_data_dir + username)
    json_file_name = json_folder_dir + f"/ifund-config.json"
    with open(json_file_name, 'r') as file:
        user_data_dict = json.loads(file.read())
    return user_data_dict or {}


def rm_user_json_data(username: str):
    global users_data_dir
    json_folder_dir = os.path.abspath(users_data_dir + username)
    json_file_name = json_folder_dir + f"/ifund-config.json"
    os.remove(json_file_name)
    return True


def edit_user_json_data(username: str, edited_json: dict):
    user_data = read_user_json_data(username)
    save_user_json_data(edited_json, username)
    return True


@logger.catch
async def change_meta5_account_password(login: str, old: str,
                                        new: str, broker:str, delay:int = 1):
    global HOST_IP
    container = create_mt5_rest_container()
    await asyncio.sleep(delay)
    mt5rest = MT5Rest()
    ##### toDo: add caching for find_broker_ips
    server = (await mt5rest.find_broker_ips(broker))[0] # getting first found server with lowest ping
    dns, dns_port = server["ip"], server["port"]
    token = await mt5rest.connect(login, old, dns, dns_port)
    response = await mt5rest.change_account_password(new)
    container.remove(force=True) 
    return response


@app.get("/")
async def root():
    return {"msg": "Welcome!"}
        
        
@logger.catch
@app.post("/containers/create", tags=["container"])
async def create_container(user: User):
    ################### initial params 
    logger.debug(f"\nnew {user = }")
    global HOST_IP
    port = generate_random_port()
    username = user.username.replace(' ', '_').strip()
    ########## toDo: add auto build accounts
    
    ######################## defining initial json data #########
    user_data_json = read_json_template()
    user_data_json["Name"] = " ".join([user.broker_userdata.first_name,
                                       user.broker_userdata.second_name])
    user_data_json["Server"] = user.broker_userdata.broker
    user_data_json["Login"] = mt5_login = ''
    user_data_json["Password"] = mt5_password = ''
    user_data_json["Investor"] = mt5_investor = ''
    user_data_json["initial_balance"] = user.broker_userdata.balance
    logger.debug(f"{user_data_json = }")
    user_json_filepath = save_user_json_data(user_data_json, username)  # saves data of config for each user
    config_dir = "/config/.wine/drive_c/users/abc/AppData/Roaming/MetaQuotes/Terminal/Common/Files"
    ##################################### building container #### 
    try:
        container = client.containers.run(mt5_image_name, 
                                          restart_policy = {"Name": "always"},
                                          detach=True, ports={3000: port},
                                          mem_limit="1g",
                                          name=username,
                                          volumes=[f"{user_json_filepath}:{config_dir}"],
                                          environment={"CUSTOM_USER": username,
                                                       "PASSWORD": user.password})
    except DockerErrors.DockerException as e:
        if hasattr(e, "status_code") & hasattr(e, "response"):
            status_code, msg = e.status_code, e.response.json()["message"]
            logger.error(e)
            raise HTTPException(status_code, msg)
    except Exception as e:
        logger.error(e)
        status_code, msg = 520, f"Error: {e}"
        raise HTTPException(status_code, msg)
    
    ###### generating entrance link #####
    url = f"{HOST_IP}:{port}"
    password = user.password
    auth_url = f'http://{username}:{password}@{url}'    
    ####################################   
    logger.debug(f"{auth_url = }")
    return {"msg": "mt5 container created",
            "ID": container.id,
            "user": {"username": username,
                     "password": password,
                     "link": auth_url,
                     "balance": user.broker_userdata.balance,
                     "mt5": {
                         "login": mt5_login,
                         "password": mt5_password,
                         "investor": mt5_investor
                     }
                     },
            "image": container.attrs['Config']['Image'],
            "port": port,
            "time_created": container.attrs["Created"]
            }


@app.get("/containers/{id}/logs/", tags=["container"])
def logs(id: str):
    try:
        _logs = PlainTextResponse(client.containers.get(id).logs())
    except DockerErrors.DockerException as e:
        if hasattr(e, "status_code") & hasattr(e, "response"):
            status_code, msg = e.status_code, e.response.json()["message"]
            raise HTTPException(status_code, msg)
    except Exception as e:
        status_code, msg = 520, f"Error: {e}"
        raise HTTPException(status_code, msg)
    return _logs


@app.put("/meta5/password/change/loginID/{id}/", tags=["meta5"])
async def change_meta_password(id:int, chpwd: ChangePassword):
    login, old, new, broker = (id, chpwd.old, chpwd.new, chpwd.broker)
    logger.debug(f"{chpwd = }")
    try:
        response = await change_meta5_account_password(login, old, new, broker)
        logger.debug(f"{response = }")
    except DockerErrors.DockerException as e:
        if hasattr(e, "status_code") & hasattr(e, "response"):
            status_code, msg = e.status_code, e.response.json()["message"]
            raise HTTPException(status_code, "DockerError: " + msg)
    except Exception as e:
        status_code, msg = 520, f"Error: {e}"
        server_names = await MT5Rest.get_broker_ServerNames(broker)
        server_msg = f", acceptable server names {server_names = }"
        raise HTTPException(status_code, msg + server_msg)
    if response == "OK":
        success_msg = f"password changed for {login = }"
        return {"msg": success_msg}
    else: 
        error_msg = f"something went wrong, mt5rest response : {response}"
        raise HTTPException(400, error_msg)
    

@app.get("/meta5/brokers/{broker:str}/", tags=["meta5"])
@app.get("/meta5/brokers/{broker:str}/servers", tags=["meta5"])
async def get_active_servers(broker: str, delay: int = 1):
    container = create_mt5_rest_container()
    await asyncio.sleep(delay)
    server_names = await MT5Rest.get_broker_ServerNames(broker)
    container.remove(force=True)
    return {"msg": f"fetched servers for {broker}", "servers": server_names}
    

@app.delete("/containers/{id}", tags=["container"])
def stop(id: str):
    try:
        container_ports = get_active_container_ports(image_name=mt5_image_name)
        client.containers.get(id).stop()
    except DockerErrors.DockerException as e:
        if hasattr(e, "status_code") & hasattr(e, "response"):
            status_code, msg = e.status_code, e.response.json()["message"]
            raise HTTPException(status_code, msg)
    except Exception as e:
        status_code, msg = 520, f"Error: {e}"
        raise HTTPException(status_code, msg)
    clear_docker_env()
    return {"msg": f"container {id} stopped at port {container_ports.get(id, None)}",
            "ID": id,
            "port": container_ports.get(id, None)}


@app.put("/containers/{id}/edit/", tags=["container"])
def edit(id: str, json_data: UserExpertData):
    try:
        username = client.containers.get(id).name
    except DockerErrors.DockerException as e:
        if hasattr(e, "status_code") & hasattr(e, "response"):
            status_code, msg = e.status_code, e.response.json()["message"]
            raise HTTPException(status_code, msg)
    except Exception as e:
        status_code, msg = 520, f"Error: {e}"
        raise HTTPException(status_code, msg)
    json_current_data = read_user_json_data(username)
    logger.debug(f"previous user data -> {json_current_data = }")
    json_input_data = json_data.model_dump(exclude_unset=True)
    logger.debug(f"new input data -> {json_input_data = }")
    new_json_data = json_current_data.copy()
    new_json_data.update(json_input_data)
    rm_user_json_data(username)
    path = save_user_json_data(new_json_data, username)
    return {"msg": f"updated user data for {username}"}


@app.get("/containers/", tags=["container"])
def list_active_containers(limit: int = 50, page: int = 1):
    max_limit = 50
    if limit > max_limit: raise HTTPException(400, f"limit must lower than {max_limit}")
    c_ids = get_active_container_ports(True, mt5_image_name)[(page-1)*limit : page*limit]
    return {"msg": "fetched active containers",
            "containers": c_ids}


@app.get("/containers/{id}", tags=["container"])
def status(id: str):
    try:
        state = client.containers.get(id).attrs["State"]
    except DockerErrors.DockerException as e:
        if hasattr(e, "status_code") & hasattr(e, "response"):
            status_code, msg = e.status_code, e.response.json()["message"]
            raise HTTPException(status_code, msg)
    except Exception as e:
        status_code, msg = 520, f"Error: {e}"
        raise HTTPException(status_code, msg)
    return {"msg": state}


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=3000)

