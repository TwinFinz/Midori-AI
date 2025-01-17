import os
import json
import yaml
import docker
import requests
import datetime

import support as s

import carly_help as help_add_on
import setup_docker as docker_add_on
import setup_models as models_add_on
import edit_models as models_edit_add_on

from colorama import Fore

from autogen import OpenAIWrapper

from cpuinfo import get_cpu_info
from multiprocessing import freeze_support

from python_on_whales import DockerClient
from python_on_whales import docker as docker_two

use_cuda = "False"
use_tts = "False"
use_core = "False"

missing_cuda = True
missing_cuda_toolkit = True

layout = None
sg = None

compose_path = "localai-docker-compose.yaml"
compose_backup_path = "docker-compose.yaml"

localai_ver_number = "v2.8.0"
base_image_name = "quay.io/go-skynet/local-ai:"

user_image = ""

answer_backup_compose ="no"

ver_info = "changemelunaplease"

ver_file_name = "midori_program_ver.txt"

about_model_size = str("""
7b - Recommend for lowerend PC (6gb of Vram or less / 10gb of system ram) - https://huggingface.co/TheBloke/dolphin-2.6-mistral-7B-GGUF
2x7b - Recommended for home PC (8gb or more of Vram needed / 25gb of system ram) - https://huggingface.co/TheBloke/laser-dolphin-mixtral-2x7b-dpo-GGUF
8x7b - Recommended for highend PC (24gb or more Vram needed / 55gb of system ram) - https://huggingface.co/TheBloke/dolphin-2.7-mixtral-8x7b-GGUF
70b - Recommended for high end servers only (AI card or better with 48gb Vram + 100gb system ram) - https://huggingface.co/TheBloke/dolphin-2.2-70B-GGUF
ID - (These are models from the Midori AI model repo) - https://io.midori-ai.xyz/models/offsite_models/
""")

about_model_q_size = str("""
| Quant Mode | Description |
|Q3| Smallest, significant quality loss - not recommended|
|Q4| Medium, balanced quality|
|Q5| Large, very low quality loss - recommended for most users|
|Q6| Very large, extremely low quality loss|
|Q8| Extremely large, extremely low quality loss, hard to use - not recommended|
|None| Extremely large, No quality loss, super hard to use - really not recommended|
                         
If unsure what you need, type ``q5``

Note: 
That some models may deviate from our conventional model formatting standards (Quantized/Non-Quantized), 
and will be served using a rounding-down approach. For instance, if you request a Q8 model and none is available, 
the Q6 model will be served instead, and so on.
""")

os.system("del model_installer.zip")
os.system("del model_installer.bat")

response_git = requests.get("https://github.com/lunamidori5/Midori-AI/blob/b9a74490f5b5ad0ecce56dbd7718fab3e31ece1b/data/version.json")

if response_git.status_code != 200:
    s.log(f"Github seem to be down, please try again in a moment...")
    exit(418)

current_version_git = response_git.text.strip()

s.log("I am setting up a temp copy of Carly...")
temp_response = help_add_on.request_info("temp_something_for_model_installer.txt")
temp_keys = temp_response.strip()
client_openai = OpenAIWrapper(base_url="https://ai.midori-ai.xyz/v1", api_key=temp_keys, timeout=6000)

# localai_ver_number = version_data['version']
ver_os_info = s.get_os_info()
# Check if the current platform is Windows

try:
    if os.name == 'nt':
         # Connect to the Docker daemon on Windows using Docker-py for Windows 
        s.log("logging into docker vm subsystem (Windows)")
        client = docker.from_env(version='auto')
    else:
        # Connect to the Docker daemon on Linux-like systems using Docker-py
        s.log("logging into docker vm subsystem (Linux)")
        s.log("If this fails please try running me as root user")
        client = docker.from_env()

except Exception as e:
    s.log("Looks like I was unable to log into the docker subsystem...")
    s.log("Do you have docker installed? / Please try running me as root user, Linux users.")
    input("Please press enter to exit: ")
    exit(1)


# List all containers
containers = client.containers.list()

s.clear_window(ver_os_info)

s.check_for_update(ver_os_info, ver_info)

s.clear_window(ver_os_info)

if os.path.exists(compose_backup_path):
    backup_compose_question = "I see that you have a ``docker-compose.yaml`` file in this folder. Is this LocalAI's docker compose file?: "
    backup_compose_valid_answers = ["yes", "no"]
        
    answer_backup_compose = s.check_str(backup_compose_question, backup_compose_valid_answers, "no", layout, sg, "This is the main menu they are asking for help on...", client_openai)

if answer_backup_compose == "yes":
    s.log("Renaming the compose file to our new safe format! Thank you!")
    s.log(f"Current file name: {compose_backup_path}")
    s.log(f"New file name: {compose_path}")
    os.rename(compose_backup_path, compose_path)
    input("Please press enter to go to main menu: ")

use_gui = "no"

while True:
    s.clear_window(ver_os_info)

    s.log("-----------------------------------------------------------------------------------------------")
    s.log(f"------------------------------ Main Menu (Ver: {ver_info}) ------------------------------------")
    s.log("-----------------------------------------------------------------------------------------------")

    s.log("``1`` - LocalAI / AnythingLLM Manager")
    s.log("``2`` - Uninstall or Upgrade LocalAI / AnythingLLM")
    s.log("``3`` - Setup or Upgrade Models")
    s.log("``4`` - Edit Models Configs")
    s.log("``5`` - Uninstall Models")
    s.log("``chat`` - Chat with Carly")
    s.log("If you need assistance with most menus, type help.")

    questionbasic = "What would you like to do?: "
    sd_valid_answers = ["1", "2", "3", "4", "5", "chat", "exit"]
        
    answerstartup = s.check_str(questionbasic, sd_valid_answers, use_gui, layout, sg, "This is the main menu they are asking for help on...", client_openai)

    if answerstartup.lower() == "exit":
        break

    if answerstartup.lower() == "chat":
        answerstartup = int(25)

    answerstartup = int(answerstartup)

    s.clear_window(ver_os_info)

    if answerstartup == 1:
        docker_add_on.setup_docker(DockerClient, compose_path, ver_os_info, containers, use_gui, sg, base_image_name, localai_ver_number, layout, client_openai)
        
    if answerstartup == 2:
        docker_add_on.change_docker(DockerClient, compose_path, ver_os_info, containers, use_gui, sg, layout, client_openai)

    if answerstartup == 3:
        models_add_on.models_install(compose_path, ver_os_info, containers, client, use_gui, sg, about_model_size, about_model_q_size, layout, client_openai)

    if answerstartup == 4:
        models_edit_add_on.edit(compose_path, ver_os_info, containers, client, use_gui, sg, layout, client_openai)

    if answerstartup == 5:
        models_add_on.models_uninstall(compose_path, ver_os_info, containers, client, use_gui, sg, layout, client_openai)

    if answerstartup == 25:
        while True:
            help_add_on.chat_room(help_add_on.request_info("system_prompt.txt"), client_openai, ver_os_info, "This is the main menu, let the user know they need to type help into other menus for you to get context")
            keep_chatting = s.check_str("Would you like to keep chatting?", ["yes", "no"], use_gui, layout, sg, "This is the main menu they are asking for help on...", client_openai)
            if keep_chatting == "no":
                break