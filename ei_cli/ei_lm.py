from threading import Thread
import os
from datetime import datetime
import json
import traceback
import requests
import urllib3
import logging
from logging import FileHandler
from logging import Formatter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_DIR = "configs"
EI_CLI_HOME = "EI_CLI_HOME"
MAX_BATCH_SIZE = os.getenv("EI_CLI_BATCH_SIZE", 20)
DEPLOY = "deploy"
UN_DEPLOY = "undeploy"
STATUS = "status"
RESET = "reset"
CHANGE_PWD = "change-pwd"

DEVICE_IP = "DEVICE_IP"
PIPELINE_NAME = "PIPELINE_NAME"
DATA_SOURCE_FILE = "DATA_SOURCE_FILE"
PIPELINE_TEMPLATE_FILE = "PIPELINE_TEMPLATE"
DATA_TARGET_FILE = "DATA_TARGET_FILE"
DATA_LOGIC_FILE = "DATA_LOGIC_FILE"
DATA_VARIABLES_FILE = "DATA_VARIABLES_FILE"

DATA_SOURCE_KEY = "dataSources"
DATA_TARGET_KEY = "dataTarget"
DATA_LOGIC_KEY = "scriptedDataLogic"
DATA_OUTPUT_MODEL_KEY = "outputModel"

PIPELINE_JSON = "PIPELINE_JSON"
RESPONSE = "RESPONSE"
PASSWORD = "PASSWORD"
NEW_PASSWORD = "NEW_PASSWORD"
OPERATION = "OPERATION"
LOGGER = "LOGGER"

BASE_URL = "/api/v2/edge-intelligence"
logger = logging.getLogger(__name__)

class EiCliThread(Thread):

  def run(self):
    self.exc = None
    try:
      if hasattr(self, '_Thread__target'):
        # Thread uses name mangling prior to Python 3.
        self.ret = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
      else:
        self.ret = self._target(*self._args, **self._kwargs)
    except BaseException as e:
      self.exc = e

  def join(self):
    super(EiCliThread, self).join()
    if self.exc:
      raise RuntimeError('Exception in thread') from self.exc
    return self.ret

def run_in_batch(task_threads, max_thread_spawns_allowed=MAX_BATCH_SIZE):
  # calculate no of batches of threads to be spawned
  if len(task_threads) > max_thread_spawns_allowed:
    if len(task_threads) % max_thread_spawns_allowed:
      no_of_batches = int(len(task_threads) / max_thread_spawns_allowed) + 1
    else:
      no_of_batches = int(len(task_threads) / max_thread_spawns_allowed)
  else:
    no_of_batches = 1
  logger.debug("No of batches of threads to run {}".format(no_of_batches))
  i = 0
  for batch in range(no_of_batches):
    # for each batch, start the threads and wait for those to complete
    if i + max_thread_spawns_allowed <= len(task_threads):
      max_t = max_thread_spawns_allowed
    else:
      max_t = max_thread_spawns_allowed - (i + max_thread_spawns_allowed - len(task_threads))
    for j in range(i, i + max_t):
      task_threads[j].start()
    # Wait for all the threads in the batch to complete
    for k in range(i, i + max_t):
      task_threads[k].join()
    i = i + max_thread_spawns_allowed

def execute_pipelines(inventory_list, operation=None, device_pwd=None,  new_password=None):
  pipeline_obj_list = []
  logger.debug("Number of objects inventory file " + str(len(inventory_list)))
  print(inventory_list)
  device_logger = get_device_logger(operation)
  # device_logger = DeviceLogger(operation)

  # Create pipeline object list from inventory list
  for inventory_obj in inventory_list:
    pipeline_obj = get_pipeline_obj(inventory_obj, operation)
    pipeline_obj[PASSWORD] = device_pwd
    pipeline_obj[NEW_PASSWORD] = new_password
    pipeline_obj[LOGGER] = device_logger
    pipeline_obj_list.append(pipeline_obj)

  # Create the pool threads for execution
  ei_cli_threads = []
  if len(pipeline_obj_list) > 0:
    for pipeline_obj in pipeline_obj_list:
      if pipeline_obj is not None:
        t = EiCliThread(target=execute_pipeline_obj, args=(operation, pipeline_obj))
        ei_cli_threads.append(t)
  # Start the thread execution in batches
  if len(ei_cli_threads) > 0:
    run_in_batch(ei_cli_threads, MAX_BATCH_SIZE)

  # Close the device logger
  # device_logger.close()

def execute_pipelinesTemplate(inventory_list, operation=None, device_pwd=None,  new_password=None):
  pipeline_obj_list = []
  logger.debug("Number of objects inventory file " + str(len(inventory_list)))
  print(inventory_list)
  device_logger = get_device_logger(operation)
  # device_logger = DeviceLogger(operation)

  # Create pipeline object list from inventory list
  for inventory_obj in inventory_list:
    pipeline_obj = get_pipeline_obj_by_template(inventory_obj, operation)
    pipeline_obj[PASSWORD] = device_pwd
    pipeline_obj[NEW_PASSWORD] = new_password
    pipeline_obj[LOGGER] = device_logger
    pipeline_obj_list.append(pipeline_obj)

  # Create the pool threads for execution
  ei_cli_threads = []
  if len(pipeline_obj_list) > 0:
    for pipeline_obj in pipeline_obj_list:
      if pipeline_obj is not None:
        t = EiCliThread(target=execute_pipeline_obj, args=(operation, pipeline_obj))
        ei_cli_threads.append(t)
  # Start the thread execution in batches
  if len(ei_cli_threads) > 0:
    run_in_batch(ei_cli_threads, MAX_BATCH_SIZE)

  # Close the device logger
  # device_logger.close()
def execute_pipeline_obj(operation=None, pipeline_obj=None):
  if operation is None:
    operation = pipeline_obj[OPERATION]
  # Check operation and perform the task
  if operation == DEPLOY:
    deploy_pipeline(pipeline_obj)
  elif operation == UN_DEPLOY:
    un_deploy_pipeline(pipeline_obj)
  elif operation == STATUS:
    get_pipeline_status(pipeline_obj)
  elif operation == CHANGE_PWD:
    change_password(pipeline_obj)
  else:
    pass

def is_valid_string(string):
  return bool(string and string.strip())

def get_pipeline_obj(inventory_obj, operation=None):
  pipeline_obj = {}
  if operation is None:
    return pipeline_obj

  device_ip = inventory_obj.get(DEVICE_IP, None)
  pipeline_name = inventory_obj.get(PIPELINE_NAME, None)

  # For any operation, device ip and pipeline name are mandatory
  if not is_valid_string(device_ip):
    logger.error("Invalid device ip given in inventory file for inventory obj " + inventory_obj)
    print("Invalid device ip given in inventory file.")
    exit(0)
  if not is_valid_string(pipeline_name):
    print("Invalid pipeline name given in inventory file.")
    logger.error("Invalid pipeline name given in inventory file for inventory obj " + inventory_obj)
    exit(0)

  # This field will contain the response of the api call and will get updated during api call execution
  pipeline_obj[RESPONSE] = "NA"
  pipeline_obj[OPERATION] = operation
  pipeline_obj[DEVICE_IP] = device_ip
  pipeline_obj[PIPELINE_NAME] = pipeline_name

  # If the operation is un-deploy or get status, then only device ip and pipeline name is needed
  if operation == STATUS or operation == UN_DEPLOY:
    return pipeline_obj

  if operation == DEPLOY:
    data_source_file = inventory_obj.get(DATA_SOURCE_FILE, None)
    data_target_file = inventory_obj.get(DATA_TARGET_FILE, None)

    # For deploy, data_source_file and data_target_file are mandatory
    if not is_valid_string(data_source_file):
      print("Invalid data source file name given in inventory file.")
      logger.error("Invalid data source file name given in inventory file for inventory obj " + inventory_obj)
      exit(0)
    if not is_valid_string(data_target_file):
      print("Invalid pipeline name given in inventory file.")
      logger.error("Invalid pipeline name given in inventory file for inventory obj " + inventory_obj)
      exit(0)

    # For deploy, data logic and data variables are not mandatory
    data_logic_file = inventory_obj.get(DATA_LOGIC_FILE, None)
    data_vars_file = inventory_obj.get(DATA_VARIABLES_FILE, None)

    # Get the pipeline json obj
    pipeline_json = get_pipeline_json(data_source_file, data_target_file, data_logic_file, data_vars_file)
    pipeline_obj[PIPELINE_JSON] = pipeline_json

  return pipeline_obj

def get_pipeline_obj_by_template(inventory_obj, operation=None):
  pipeline_obj = {}
  if operation is None:
    return pipeline_obj

  device_ip = inventory_obj.get(DEVICE_IP, None)
  pipeline_name = inventory_obj.get(PIPELINE_NAME, None)

  # For any operation, device ip and pipeline name are mandatory
  if not is_valid_string(device_ip):
    logger.error("Invalid device ip given in inventory file for inventory obj " + inventory_obj)
    print("Invalid device ip given in inventory file.")
    exit(0)
  if not is_valid_string(pipeline_name):
    print("Invalid pipeline name given in inventory file.")
    logger.error("Invalid pipeline name given in inventory file for inventory obj " + inventory_obj)
    exit(0)

  # This field will contain the response of the api call and will get updated during api call execution
  pipeline_obj[RESPONSE] = "NA"
  pipeline_obj[OPERATION] = operation
  pipeline_obj[DEVICE_IP] = device_ip
  pipeline_obj[PIPELINE_NAME] = pipeline_name

  # If the operation is un-deploy or get status, then only device ip and pipeline name is needed
  if operation == STATUS or operation == UN_DEPLOY:
    return pipeline_obj

  if operation == DEPLOY:
    pipeline_template_file = inventory_obj.get(PIPELINE_TEMPLATE_FILE, None)


    # For deploy, data_source_file and data_target_file are mandatory
    if not is_valid_string(pipeline_template_file):
      print("Invalid pipeline template file name given in inventory file.")
      logger.error("Invalid  pipeline template file name given in inventory file for inventory obj " + inventory_obj)
      exit(0)
    #
    # # For deploy, data logic and data variables are not mandatory
    # data_logic_file = inventory_obj.get(DATA_LOGIC_FILE, None)
    # data_vars_file = inventory_obj.get(DATA_VARIABLES_FILE, None)

    # Get the pipeline json obj
    pipeline_json = get_pipeline_template_json(pipeline_template_file)
    pipeline_obj[PIPELINE_JSON] = pipeline_json

  return pipeline_obj

def read_json_file(file_name):
  data = None
  if file_name is None:
    return data
  file_path = os.path.join(os.getenv(EI_CLI_HOME), CONFIG_DIR, file_name)
  with open(file_path, 'r') as file:
    data = json.load(file)
  return data

def get_pipeline_json(data_source_file, data_target_file, data_logic_file=None, data_vars_file=None):
  pipeline_json = dict()
  data_source_json = read_json_file(data_source_file)
  data_target_json = read_json_file(data_target_file)
  data_logic_json = read_json_file(data_logic_file)
  data_vars_json = read_json_file(data_vars_file)
  pipeline_json[DATA_SOURCE_KEY] = data_source_json[DATA_SOURCE_KEY]
  pipeline_json[DATA_TARGET_KEY] = data_target_json[DATA_TARGET_KEY]
  if DATA_OUTPUT_MODEL_KEY in data_target_json:
    pipeline_json[DATA_OUTPUT_MODEL_KEY] = data_target_json[DATA_OUTPUT_MODEL_KEY]
  if data_logic_json is not None:
    pipeline_json[DATA_LOGIC_KEY] = data_logic_json[DATA_LOGIC_KEY]

  # Apply template variables if applicable
  if data_vars_json is not None:
    logger.debug("Pipeline Json before templatization " + json.dumps(pipeline_json) + " " + data_vars_file)
    path_dict = dict()
    for key, value in data_vars_json.items():
      key = "$" + key
      # pipeline_json_str = pipeline_json_str.replace(temp_var, str(value))
      # paths = list()
      # paths = get_var_key_paths(pipeline_json, path_list=paths, path_key=key)
      # print(key, ":", paths)
      # path_dict = update_var_key_path_dict(obj=pipeline_json, path_dict=path_dict, path_key=key, path_value=value)
      pipeline_json = update_pipeline_obj_dict(obj=pipeline_json, path_key=key, path_value=value)
    logger.debug("Pipeline Json after templatization " + json.dumps(pipeline_json))
  return pipeline_json

def get_pipeline_template_json(pipeline_template_file, data_vars_file=None):
  pipeline_json = dict()
  pipeline_template_json = read_json_file(pipeline_template_file)
  data_vars_json = read_json_file(data_vars_file)

  # Apply template variables if applicable
  if data_vars_json is not None:
    logger.debug("Pipeline Json before templatization " + json.dumps(pipeline_json) + " " + data_vars_file)
    path_dict = dict()
    for key, value in data_vars_json.items():
      key = "$" + key
      # pipeline_json_str = pipeline_json_str.replace(temp_var, str(value))
      # paths = list()
      # paths = get_var_key_paths(pipeline_json, path_list=paths, path_key=key)
      # print(key, ":", paths)
      # path_dict = update_var_key_path_dict(obj=pipeline_json, path_dict=path_dict, path_key=key, path_value=value)
      pipeline_json = update_pipeline_obj_dict(obj=pipeline_json, path_key=key, path_value=value)
    logger.debug("Pipeline Json after templatization " + json.dumps(pipeline_json))
  return pipeline_json

def update_pipeline_obj_dict(obj, prefix='', path_key="", path_value=""):
  if isinstance(obj, dict):
    for k, v in obj.items():
      p = "{}[{}]".format(prefix, k)
      update_pipeline_obj_dict(v, prefix=p, path_key=path_key, path_value=path_value)
      # if v == "$MQTT_QOS" or v == "$INVOKE_INTERVAL":
      if v == path_key:
        p = p.replace("{}", "")
        obj[k] = path_value
        print('{} = {} = {}'.format(v, p, path_value))
  elif isinstance(obj, list):
    # This is to add index of array to the paths
    for i, v in enumerate(obj):
      p = "{}[{}]".format(prefix, i)
      update_pipeline_obj_dict(v, prefix=p, path_key=path_key, path_value=path_value)
  else:
    pass
    # print('{} = {}'.format(prefix, repr(v)))
  return obj

def update_var_key_path_dict(obj, prefix='', path_dict=dict(), path_key="", path_value=""):
  if isinstance(obj, dict):
    for k, v in obj.items():
      p = "{}[{}]".format(prefix, k)
      update_var_key_path_dict(v, prefix=p, path_dict=path_dict, path_key=path_key, path_value=path_value)
      # if v == "$MQTT_QOS" or v == "$INVOKE_INTERVAL":
      if v == path_key:
        p = p.replace("{}", "")
        path_dict[p] = v
        obj[k] = path_value
        print('{} = {}'.format(v, p))
        print("Key:", v, "Value:", path_value, "Path:", p)
  elif isinstance(obj, list):
    # This is to add index of array to the paths
    for i, v in enumerate(obj):
      p = "{}[{}]".format(prefix, i)
      update_var_key_path_dict(v, prefix=p, path_dict=path_dict, path_key=path_key, path_value=path_value)
  else:
    pass
    # print('{} = {}'.format(prefix, repr(v)))
  return path_dict

def get_var_key_paths(obj, prefix='', path_key="", path_list=[]):
  if isinstance(obj, dict):
    for k, v in obj.items():
      p = "{}[{}]".format(prefix, k)
      get_var_key_paths(v, prefix=p, path_key=path_key, path_list=path_list)
      # if v == "$MQTT_QOS" or v == "$INVOKE_INTERVAL":
      if v == path_key:
        # Path is starting with {}, replace with empty string
        path = p.replace("{}", "")
        path_list.append(path)
        # print('{} = {}'.format(path_key, repr(path_list)))
  elif isinstance(obj, list):
    # This is to add index of array to the paths
    for i, v in enumerate(obj):
      p = "{}[{}]".format(prefix, i)
      get_var_key_paths(v, prefix=p, path_key=path_key, path_list=path_list)
  else:
    pass
    # print('{} = {}'.format(prefix, repr(v)))
  return path_list

def check_paths(obj, path_list, path_key, path_value):
  # Path list contains str representation of array
  # $INVOKE_INTERVAL : ['[scriptedDataLogic][invokeEvery]']
  # $MQTT_QOS : ['[dataTarget][dataTargetConfiguration][connectors][0][mqttQoS]', '[dataTarget][dataTargetConfiguration][connectors][0][publish][resultPath][mqttQos]']
  print("-------------", path_key, "-------------")
  for path_str in path_list:
    # Remove first and last characters which are '[' and ']'
    path_str = path_str.replace('[', '', 1)
    path_str = path_str[:-1]
    paths = path_str.split("][")
    print(paths)
    print("----------------------------------------")

def get_pipeline_status(pipeline_obj):
  device_ip = pipeline_obj[DEVICE_IP]
  device_pwd = pipeline_obj[PASSWORD]
  dev_logger = pipeline_obj[LOGGER]
  pipeline_name = pipeline_obj[PIPELINE_NAME]
  logger.debug("Started getting pipeline status for " + pipeline_name + " on device " + device_ip)
  print("Started getting pipeline status for", pipeline_name, "on device", device_ip)
  try:
    access_token = get_access_token(device_ip, password=device_pwd)
    url = "https://" + device_ip + BASE_URL + "/pipelines/" + pipeline_name + "/status"
    headers = {
      'Authorization': 'Bearer ' + access_token,
      'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers, verify=False)
    res_json = json.loads(response.text.encode('utf8'))
    res_code = response.status_code
    pipeline_status = "NA"
    # Check for status
    if res_code == 200:
      status = pipeline_obj[STATUS] = "Success"
      message = pipeline_obj[RESPONSE] = "Status Code: " + str(res_code) + ", Response: " + str(res_json)
      logger.debug("Successfully got pipeline status for " + pipeline_name + " on device " + device_ip + " " + message)
      pipeline_status = res_json.get('data').get('healthStatus').get('pipelineStatus')
    else:
      # res_code != 200:
      status = pipeline_obj[STATUS] = "Failed"
      message = pipeline_obj[RESPONSE] = "Status Code: " + str(res_code) + ", Response: " + str(res_json)
      logger.debug("Error in getting pipeline status for " + pipeline_name + " on device " + device_ip + " " + message)
  except Exception as ex:
    status = pipeline_obj[STATUS] = "Failed"
    message = pipeline_obj[RESPONSE] = str(ex)
    logger.debug("Exception in get pipeline status for " + pipeline_name + " on device " + device_ip + " " + str(ex))

  dev_logger.info("pipeline status " + pipeline_name + " on device " + device_ip + " -> Status: " + status + ", " + message)
  if status == "Success":
    print("Finished getting pipeline status for " + pipeline_name + " on device " + device_ip + " Status: " + pipeline_status)
    logger.debug("Finished getting pipeline status for " + pipeline_name + " on device " + device_ip + " Status: " + pipeline_status)
  else:
    print("Finished getting pipeline status for " + pipeline_name + " on device " + device_ip + " Status: " + status)
    logger.debug("Finished getting pipeline status for " + pipeline_name + " on device " + device_ip + " Status: " + status)

def deploy_pipeline(pipeline_obj):
  device_ip = pipeline_obj[DEVICE_IP]
  device_pwd = pipeline_obj[PASSWORD]
  dev_logger = pipeline_obj[LOGGER]
  pipeline_name = pipeline_obj[PIPELINE_NAME]
  pipeline_json = pipeline_obj[PIPELINE_JSON]
  logger.debug("Started deploying pipeline " + pipeline_name + " on device " + device_ip)
  print("Started deploying pipeline", pipeline_name, "on device", device_ip)
  try:
    access_token = get_access_token(device_ip, password=device_pwd)
    url = "https://" + device_ip + BASE_URL + "/pipelines"
    headers = {
      'Authorization': 'Bearer ' + access_token,
      'Content-Type': 'application/json'
    }
    post_data = {
      "name": pipeline_name,
      "data": pipeline_json
    }
    logger.debug("Pipeline Json for " + pipeline_name + " on device " + device_ip)
    logger.debug(json.dumps(post_data))
    logger.debug("===========================================================================================")
    response = requests.post(url=url, data=json.dumps(post_data), headers=headers, verify=False)
    res_json = json.loads(response.text.encode('utf8'))
    res_code = response.status_code
    # Check for status
    if res_code == 200:
      status = pipeline_obj[STATUS] = "Success"
      message = pipeline_obj[RESPONSE] = "Status Code: " + str(res_code) + ", Response: " + str(res_json)
      logger.debug("Successfully deployed the pipeline " + pipeline_name + " on device " + device_ip + " " + message)
    else:
      # res_code != 200:
      status = pipeline_obj[STATUS] = "Failed"
      message = pipeline_obj[RESPONSE] = "Status Code: " + str(res_code) + ", Response: " + str(res_json)
      logger.debug("Error deploying the pipeline " + pipeline_name + " on device " + device_ip + " " + message)
  except Exception as ex:
    status = pipeline_obj[STATUS] = "Failed"
    message = pipeline_obj[RESPONSE] = str(ex)
    logger.debug("Exception in deploy pipeline for " + pipeline_name + " on device " + device_ip + " " + str(ex))

  dev_logger.info("deploy pipeline " + pipeline_name + " on device " + device_ip + " -> Status: " + status + ", " + message)
  print("Finished deploying pipeline " + pipeline_name + " on device " + device_ip + " Status: " + status)
  logger.debug("Finished deploying pipeline " + pipeline_name + " on device " + device_ip + " Status: " + status)

def un_deploy_pipeline(pipeline_obj):
  device_ip = pipeline_obj[DEVICE_IP]
  device_pwd = pipeline_obj[PASSWORD]
  dev_logger = pipeline_obj[LOGGER]
  pipeline_name = pipeline_obj[PIPELINE_NAME]
  logger.debug("Started un-deploying pipeline " + pipeline_name + " on device " + device_ip)
  print("Started un-deploying pipeline", pipeline_name, "on device", device_ip)
  try:
    access_token = get_access_token(device_ip, password=device_pwd)
    url = "https://" + device_ip + BASE_URL + "/pipelines/" + pipeline_name
    headers = {
      'Authorization': 'Bearer ' + access_token,
      'Content-Type': 'application/json'
    }
    response = requests.delete(url=url, headers=headers, verify=False)
    res_json = json.loads(response.text.encode('utf8'))
    res_code = response.status_code
    # Check for status
    if res_code == 200:
      status = pipeline_obj[STATUS] = "Success"
      message = pipeline_obj[RESPONSE] = "Status Code: " + str(res_code) + ", Response: " + str(res_json)
      logger.debug("Successfully un-deployed pipeline for " + pipeline_name + " on device " + device_ip + " " + message)
    else:
      # res_code != 200:
      status = pipeline_obj[STATUS] = "Failed"
      message = pipeline_obj[RESPONSE] = "Status Code: " + str(res_code) + ", Response: " + str(res_json)
      logger.debug("Error in un-deploy pipeline for " + pipeline_name + " on device " + device_ip + " " + message)
  except Exception as ex:
    status = pipeline_obj[STATUS] = "Failed"
    message = pipeline_obj[RESPONSE] = str(ex)
    logger.debug("Exception in un-deploy pipeline for " + pipeline_name + " on device " + device_ip + " " + str(ex))

  dev_logger.info("un-deploy pipeline " + pipeline_name + " on device " + device_ip + " -> Status: " + status + ", " + message)
  print("Finished un-deploying pipeline " + pipeline_name + " on device " + device_ip + " Status: " + status)
  logger.debug("Finished un-deploying pipeline " + pipeline_name + " on device " + device_ip + " Status: " + status)

def change_password(pipeline_obj):
  device_ip = pipeline_obj[DEVICE_IP]
  username = "admin"
  old_device_pwd = pipeline_obj[PASSWORD]
  new_device_pwd = pipeline_obj[NEW_PASSWORD]
  dev_logger = pipeline_obj[LOGGER]
  logger.debug("Started changing password on device " + device_ip)
  print("Started changing password on device " + device_ip)
  url = "https://" + device_ip + BASE_URL + "/change-password"
  post_data = {
    "username": username,
    "old_password": old_device_pwd,
    "new_password": new_device_pwd
  }
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url=url, data=json.dumps(post_data), headers=headers, verify=False)
    res_json = json.loads(response.text.encode('utf8'))
    res_code = response.status_code
    if res_code == 200:
      status = pipeline_obj[STATUS] = "Success"
      message = pipeline_obj[RESPONSE] = "Http Code: " + str(res_code) + ", Response: " + str(res_json)
      logger.debug("Password updated successfully for device " + device_ip + " " + message)
    else:
      # res_code != 200:
      status = pipeline_obj[STATUS] = "Failed"
      message = pipeline_obj[RESPONSE] = "Http Code: " + str(res_code) + ", Response: " + str(res_json)
      logger.debug("Error updating password for device " + device_ip + " " + message)
  except Exception as ex:
    status = pipeline_obj[STATUS] = "Failed"
    message = pipeline_obj[RESPONSE] = str(ex)
    logger.debug("Exception in change_password for " + device_ip + " " + str(ex))

  dev_logger.info("change-pwd on device " + device_ip + " -> Status: " + status + ", " + message)
  logger.debug("Finished changing password on device " + device_ip + " Status: " + status)
  print("Finished changing password on device " + device_ip + " Status: " + status)

def get_access_token(device_ip, username="admin", password="None"):
  access_token = None
  url = "https://" + device_ip + BASE_URL + "/token"
  print("fetching token for device " + url)
  post_data = {
    "username": username,
    "password": password
  }
  print("fetching token for device " + post_data)
  logger.debug("Fetching access token for device " + device_ip)
  try:
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url=url, data=json.dumps(post_data), headers=headers, verify=False)
    res_json = json.loads(response.text.encode('utf8'))
    res_code = response.status_code
    if res_code == 200:
      access_token = res_json.get('data').get('token')
    else:
      # res_code != 200:
      logger.debug("Error fetching token for device " + device_ip + str(res_code) + str(res_json))
      print("Error fetching token for device " + device_ip + " Response: " + str(res_json))
      raise Exception("Error fetching token for device " + device_ip + " Response: " + str(res_json))
  except Exception as ex:
    logger.debug("Exception in get_access_token for device " + device_ip + " " + str(ex))
    raise Exception("Exception in get_access_token for device " + device_ip + " " + str(ex))

  return access_token

def get_device_logger(operation):
  log_file_name = operation + "_" + datetime.today().strftime('%Y%m%d_%H%M%S') + ".log"
  log_file_name = log_file_name.replace("-", "_")
  device_log_file = os.path.join(os.getenv("EI_CLI_HOME"), log_file_name)
  device_logger = logging.getLogger("device_logger")
  device_logger.setLevel(logging.INFO)
  device_logger_file_handler = FileHandler(device_log_file)
  device_logger_file_handler.setLevel(logging.INFO)
  device_logger_file_handler.setFormatter(Formatter('%(asctime)s %(message)s'))
  device_logger.addHandler(device_logger_file_handler)
  return device_logger

class DeviceLogger:
  def __init__(self, operation):
    log_file_name = operation + "_" + datetime.today().strftime('%Y%m%d_%H%M%S') + ".log"
    log_file_name = log_file_name.replace("-", "_")
    log_file_path = os.path.join(os.getenv("EI_CLI_HOME"), log_file_name)
    self.file_obj = open(log_file_path, "w")

  def info(self, message):
    try:
      # print(message)
      self.file_obj.write(message + "\n")
      logger.info("Device Log: " + message)
    except:
      print(traceback.format_exc())
      print("Warning: Unable to write to the device log file")
      logger.error(traceback.format_exc())

  def close(self):
    try:
      print("")
      self.file_obj.close()
    except:
      logger.error(traceback.format_exc())

if __name__ == '__main__':
  source_file = "test_data_source_1.json"
  target_file = "test_data_target_1.json"
  logic_file = "test_data_logic_1.json"
  vars_file = "test_data_vars_1.json"
  pipe_line_json = get_pipeline_json(source_file, target_file, logic_file, vars_file)
  print(pipe_line_json)
