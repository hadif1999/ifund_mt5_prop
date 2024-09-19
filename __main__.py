import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
import uvicorn
import os
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
from src.schemas import User, UserExpertData
from src.mt5_rest import MT5Rest

app = FastAPI()
client = docker.from_env()
mt5_image_name = "hadi1999/meta5_custom_minimal:latest"
users_data_dir = "./data/users/"  # keep using / at end
HOST_IP = "51.89.168.20"


def build_image(image_name: str):
    image = client.images.pull(image_name)
    return image.short_id


def current_image_name_list() -> list[str]:
    name_list = [" ".join(image.attrs['RepoTags'])
                 for image in client.images.list()]
    return name_list


def image_exists(tag_name):
    return any([tag_name in img_name
                for img_name in current_image_name_list()])
    
    
def get_image_name_from_container(container: Container) -> str:
    image_name = client.images.get(container.attrs['Image']).attrs['RepoTags'][0]
    return image_name


def generate_random_port(start: int = 4000, end: int = 7000):
    unique = False
    while not unique:
        port = random.randint(start, end)
        unique = port not in get_allocated_ports()
    return port


def read_json_template(directory: str = '.', name: str = "ifund-config.json"):
    with open(f"{directory}/{name}", "r") as file:
        conf_dict = json.loads(file.read())
    return conf_dict


def get_allocated_ports():
    return list(get_active_container_ports().values())


def get_active_container_ids():
    return list(get_active_container_ports().keys())


def get_active_container_ports(
        to_list: bool = False,
        image_name: str|None = None):  
    # dict of containers by container id and port container_dict[id] = port
    container_dict = {}
    containers = client.containers.list()
    for c in containers:
        if image_name: # checking image if provided, adding container to output if equal images
            image_name_used = get_image_name_from_container(c)
            if image_name_used != image_name: continue
        id = c.id
        container_port = None
        ports = c.ports
        for port in ports: # extracting container port
            if None in ports[port]: continue
            for p in ports[port]:
                if p["HostPort"].isdigit():
                    container_port = p["HostPort"]
                    break
            if container_port:
                container_dict[id] = container_port
                break
    if to_list:
        container_ls = [{"id": c_id, "port": port} 
                        for c_id, port in container_dict.items()]
        return container_ls
    return container_dict


def get_container_userpass_from_id(id: str):
    envs = client.containers.get(id).attrs["Config"]["Env"]
    password = [env.split('=')[1] for env in envs if "PASSWORD" in env][0]
    username = [env.split('=')[1] for env in envs if "CUSTOM_USER" in env][0]
    return {"username": username, "password": password}



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
    return user_data_dict


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


def create_mt5_rest_container() -> Container:
    container = client.containers.run(MT5Rest.IMAGE_NAME, auto_remove = True,
                                      detach=True, ports={80: MT5Rest.PORT}, 
                                      name="mt5rest", mem_limit="1g")
    return container


async def change_meta5_account_password(login: str, old: str, new: str, delay:int = 1):
    container = create_mt5_rest_container()
    time.sleep(delay)
    ip = container.attrs['NetworkSettings']['IPAddress']
    MT5Rest.HOST = ip
    mt5rest = MT5Rest()
    token = await mt5rest.connect(login, old)
    response = await mt5rest.change_account_password(new)
    assert "OK" in response and len(token) > 1, "something went wrong when changing password" 
    return response


@app.get("/")
async def root():
    return {"msg": "Welcome!"}


@asynccontextmanager
async def startup_callback(app: FastAPI):
    image_names = [mt5_image_name, MT5Rest.IMAGE_NAME]
    for image_name in image_names:
        if not image_exists(image_name):
            try:
                build_image(image_name)
            except Exception as e:
                raise e
    


@app.post("/containers/create")
async def create_container(user: User, bgts:BackgroundTasks):
    logger.debug(f"\nnew {user = }")
    global HOST_IP
    port = generate_random_port()
    username = user.username.replace(' ', '_').strip()
    ######################## defining initial json data #########
    user_data_json = read_json_template()
    user_data_json["Name"] = " ".join([user.broker_userdata.first_name,
                                       user.broker_userdata.second_name])
    user_data_json["Server"] = user.broker_userdata.broker
    user_data_json["Login"] = None
    user_data_json["Password"] = None
    user_data_json["Investor"] = None
    user_data_json["initial_balance"] = user.broker_userdata.balance
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
            raise HTTPException(status_code, msg)
    except Exception as e:
        status_code, msg = 520, f"Error: {e}"
        raise HTTPException(status_code, msg)
    ########################## adding pass and user to json ##########
    mt5_login = ''
    mt5_password = ''
    mt5_investor = ''
    user_data_json["Login"] = mt5_login
    user_data_json["Password"] = mt5_password
    user_data_json["Investor"] = mt5_investor
    user_data_json["initial_balance"] = user.broker_userdata.balance
    user_json_filepath = save_user_json_data(user_data_json, username)
    url = f"{HOST_IP}:{port}"
    password = user.password
    auth_url = f'http://{username}:{password}@{url}'
    print(f"{auth_url = }")
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


@app.get("/containers/logs/{id}")
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


@app.get("/containers/meta5/password/change/{id}")
def change_meta_password(id: str, old: str, new: str, login: int|str,
                         bgts:BackgroundTasks, delay = 1):
    try:
        bgts.add_task(change_meta5_account_password, login, old, new, delay)
    except DockerErrors.DockerException as e:
        if hasattr(e, "status_code") & hasattr(e, "response"):
            status_code, msg = e.status_code, e.response.json()["message"]
            raise HTTPException(status_code, msg)
    except Exception as e:
        status_code, msg = 520, f"Error: {e}"
        raise HTTPException(status_code, msg)
    return {"msg": f"password changed for container {id}"}


@app.delete("/containers/{id}")
def stop(id: str):
    try:
        container_ports = get_active_container_ports()
        client.containers.get(id).stop()
    except DockerErrors.DockerException as e:
        if hasattr(e, "status_code") & hasattr(e, "response"):
            status_code, msg = e.status_code, e.response.json()["message"]
            raise HTTPException(status_code, msg)
    except Exception as e:
        status_code, msg = 520, f"Error: {e}"
        raise HTTPException(status_code, msg)
    client.volumes.prune()
    client.containers.prune()
    return {"msg": f"container {id} stopped at port {container_ports.get(id, None)}",
            "ID": id,
            "port": container_ports.get(id, None)}


@app.put("/containers/edit/{id}")
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
    json_input_data = json_data.model_dump(exclude_unset=True,
                                           exclude_none=True)
    new_json_data = json_current_data.copy().update(json_input_data)
    rm_user_json_data(username)
    path = save_user_json_data(new_json_data, username)
    return {"msg": f"updated user data for {username}"}


@app.get("/containers/")
def list_active_containers(limit: int = 50, page: int = 1):
    c_ids = get_active_container_ports(True, mt5_image_name)[(page-1)*limit : page*limit]
    return {"msg": "fetched active containers",
            "containers": c_ids}


@app.get("/containers/{id}")
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
    uvicorn.run(app=app, host="0.0.0.0", port=3000, lifespan=startup_callback)

