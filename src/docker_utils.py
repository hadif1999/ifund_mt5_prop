import docker 
from docker import errors as DockerErrors
from docker.models.containers import Container
from src.mt5_rest import MT5Rest


client = docker.from_env()
mt5_image_name = "hadi1999/meta5_custom_minimal:latest"


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


def create_mt5_rest_container() -> Container:
    container = client.containers.run(MT5Rest.IMAGE_NAME, auto_remove = True,
                                      detach=True, ports={80: MT5Rest.PORT}, 
                                      name="mt5rest", mem_limit="1g")
    return container


def clear_docker_env():
    client.containers.prune()
    client.volumes.prune()

