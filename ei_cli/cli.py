#!/usr/bin/env python3

"""Command Line Module for EI Local Manager Orchestration"""

import argparse
import getpass
import logging
import os
import shutil
import sys
import traceback
import yaml

from ei_cli import ei_lm
from ei_cli.version import VERSION

#import ei_lm
#from version import VERSION

logger = logging.getLogger(__name__)
CONFIG_DIR = "configs"
SAMPLE_DIR = "sample"
EI_CLI_HOME = "EI_CLI_HOME"

def configure_logging():
  if os.getenv("EI_CLI_HOME") is None:
    print("EI_CLI_HOME env variable is not set. Please set the EI_CLI_HOME env variable")
    exit(0)
  _config_dir = os.getenv("EI_CLI_HOME", ".ei")
  log_path = os.path.join(_config_dir, 'ei-cli.log')
  if not os.path.exists(os.path.dirname(log_path)):
    try:
      os.makedirs(os.path.dirname(log_path), exist_ok=True)
    except:
      print("[ERROR]: Failed to create log directory", log_path)
  elif (os.path.exists(log_path) and not os.access(log_path, os.W_OK)) or not os.access(os.path.dirname(log_path), os.W_OK):
    print("[WARNING]: log file at %s is not writeable and we cannot create it\n" % log_path, file=sys.stderr)
  else:
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s %(name)s %(message)s')
  os.environ['EI_LOG_PATH'] = log_path

def main():
  # Configure the default logging
  configure_logging()

  # Configure the CLI parameters
  parser = argparse.ArgumentParser(description="EI Local Manager CLI Orchestrator [Version " + VERSION + "]")
  command_parser = parser.add_subparsers(help="options", dest='command')
  # CLI to initialize the ei-cli environment
  init_parser = command_parser.add_parser('init', help='initialize ei-cli environment')

  # User related CLIs
  user_parser = command_parser.add_parser('user', help='user operations (change-password)')
  user_command_parser = user_parser.add_subparsers(dest='user_command')

  user_change_pwd_parser = user_command_parser.add_parser('change-pwd', help='change user(s) password on the device(s)')
  user_change_pwd_parser.add_argument('-f', '--file', type=str, dest='inventory_file', help='device(s) inventory file (yaml)')

  # Agent related CLIs
  agent_parser = command_parser.add_parser('agent', help='agent operations (status, reset)')
  agent_command_parser = agent_parser.add_subparsers(dest='agent_command')

  agent_reset_parser = agent_command_parser.add_parser('reset', help='reset the agent(s)')
  agent_reset_parser.add_argument('-f', '--file', type=str, dest='inventory_file', help='device(s) inventory file (yaml)')

  agent_status_parser = agent_command_parser.add_parser('status', help='get status of the agent(s)')
  agent_status_parser.add_argument('-f', '--file', type=str, dest='inventory_file', help='device(s) inventory file (yaml)')

  # Pipeline related CLIs
  pipeline_parser = command_parser.add_parser('pipeline', help='pipeline operations (deploy, undeploy, status)')
  pipeline_command_parser = pipeline_parser.add_subparsers(dest='pipeline_command')

  pipeline_deploy_parser = pipeline_command_parser.add_parser('deploy', help='deploy data pipeline(s)')
  pipeline_deploy_parser.add_argument('-f', '--file', type=str, dest='inventory_file', help='pipeline(s) inventory file (yaml)')

  pipeline_deploy_parser = pipeline_command_parser.add_parser('deploy-template', help='deploy data pipeline(s)')
  pipeline_deploy_parser.add_argument('-f', '--file', type=str, dest='inventory_file', help='pipeline(s) inventory file (yaml)')

  pipeline_undeploy_parser = pipeline_command_parser.add_parser('undeploy', help='un-deploy data pipeline(s)')
  pipeline_undeploy_parser.add_argument('-f', '--file', type=str, dest='inventory_file', help='pipeline(s) inventory file (yaml)')

  pipeline_status_parser = pipeline_command_parser.add_parser('status', help='get status of data pipeline(s)')
  pipeline_status_parser.add_argument('-f', '--file', type=str, dest='inventory_file', help='pipeline(s) inventory file (yaml)')

  cli_args = parser.parse_args()
  logger.debug("EI CLI command running with args: %s", vars(cli_args))

  if cli_args.command == 'init':
    on_cli_init(vars(cli_args), init_parser)
  elif cli_args.command == 'pipeline':
    if cli_args.pipeline_command == 'deploy':
      on_pipeline_deploy(vars(cli_args), pipeline_deploy_parser)
    elif cli_args.pipeline_command == 'undeploy':
      on_pipeline_undeploy(vars(cli_args), pipeline_undeploy_parser)
    elif cli_args.pipeline_command == 'status':
      on_pipeline_status(vars(cli_args), pipeline_status_parser)
    elif cli_args.pipeline_command == 'deploy-template':
      on_pipeline_deploy_template(vars(cli_args), pipeline_deploy_parser)
    else:
      parser.print_help()
  elif cli_args.command == 'agent':
    if cli_args.agent_command == 'reset':
      on_agent_reset(vars(cli_args), agent_reset_parser)
    elif cli_args.agent_command == 'status':
      on_agent_status(vars(cli_args), agent_status_parser)
    else:
      parser.print_help()
  elif cli_args.command == 'user':
    if cli_args.user_command == 'change-pwd':
      on_user_change_pwd(vars(cli_args), user_change_pwd_parser)
    else:
      parser.print_help()
  else:
    parser.print_help()

def is_valid_string(string):
  return bool(string and string.strip())

def on_cli_init(cli_args, parser):
  logger.debug("Calling on_cli_init()")
  try:
    status = init_ei_cli()
    if status:
      print("EI CLI env successfully initialized at '{}'".format(os.getenv(EI_CLI_HOME)))
      logger.debug("EI CLI env initialization successful at EI_CLI_HOME : '{}'".format(os.getenv(EI_CLI_HOME)))
    else:
      print("Failed to initialize EI CLI env at '{}'".format(os.getenv(EI_CLI_HOME)))
      logger.debug("EI CLI env initialization failed at EI_CLI_HOME : '{}'".format(os.getenv(EI_CLI_HOME)))
  except Exception as ex:
    logger.debug("EI CLI initialization failed :" + str(ex))
    print("EI CLI initialization failed : " + str(ex))

def copytree(src, dst, symlinks=False, ignore=None):
  for item in os.listdir(src):
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if os.path.isdir(s):
      shutil.copytree(s, d, symlinks, ignore)
    else:
      shutil.copy2(s, d)

def init_ei_cli():
  # Check EI_CLI_HOME env is set or not
  if os.getenv(EI_CLI_HOME) is None:
    raise Exception("EI_CLI_HOME env variable is not set")
  dest_config_dir = os.path.join(os.getenv(EI_CLI_HOME), CONFIG_DIR, SAMPLE_DIR)
  src_config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_DIR, SAMPLE_DIR)
  if not os.path.exists(dest_config_dir):
    os.makedirs(dest_config_dir)
  # print("Copying sample configs files from " + src_config_dir + " to " + dest_config_dir)
  logger.debug("Copying sample configs files from " + src_config_dir + " to " + dest_config_dir)
  # shutil.copytree(src_config_dir, dest_config_dir, dirs_exist_ok=True)  # This works with python 3.8 and above
  copytree(src_config_dir, dest_config_dir)
  return True

def on_pipeline_deploy(cli_args, parser):
  logger.debug("Calling on_pipeline_deploy()")
  inventory_file = cli_args.get("inventory_file", "")
  if is_valid_string(inventory_file):
    common_password = getpass.getpass('Enter the password:')
    logger.debug("Pipeline deploy selected for " + inventory_file)
    try:
      inventory_data = load_inventory(file_name=inventory_file)
      ei_lm.execute_pipelines(inventory_data, operation=ei_lm.DEPLOY, device_pwd=common_password)
    except Exception as ex:
      print(traceback.format_exc())
      logger.error(traceback.format_exc())
  else:
    print("\nPlease provide a valid pipeline inventory file option\n")
    logger.error("Invalid : pipeline inventory file options :" + str(inventory_file))
    parser.print_help()

def on_pipeline_deploy_template(cli_args, parser):
  logger.debug("Calling on_pipeline_deploy_template()")
  inventory_file = cli_args.get("inventory_file", "")
  if is_valid_string(inventory_file):
    common_password = getpass.getpass('Enter the password:')
    logger.debug("Pipeline deploy selected for " + inventory_file)
    try:
      inventory_data = load_inventory(file_name=inventory_file)
      ei_lm.execute_pipelinesTemplate(inventory_data, operation=ei_lm.DEPLOY, device_pwd=common_password)
    except Exception as ex:
      print(traceback.format_exc())
      logger.error(traceback.format_exc())
  else:
    print("\nPlease provide a valid pipeline inventory file option\n")
    logger.error("Invalid : pipeline inventory file options :" + str(inventory_file))
    parser.print_help()
def on_pipeline_undeploy(cli_args, parser):
  logger.debug("Calling on_pipeline_undeploy()")
  common_password = getpass.getpass('Enter the password:')
  inventory_file = cli_args.get("inventory_file", "")
  if is_valid_string(inventory_file):
    logger.debug("Pipeline un-deploy selected for " + inventory_file)
    try:
      inventory_data = load_inventory(file_name=inventory_file)
      ei_lm.execute_pipelines(inventory_data, operation=ei_lm.UN_DEPLOY, device_pwd=common_password)
    except Exception as ex:
      print(ex)
  else:
    print("\nPlease provide a valid pipeline inventory file option\n")
    logger.error("Invalid : pipeline inventory file options :" + str(inventory_file))
    parser.print_help()

def on_pipeline_status(cli_args, parser):
  logger.debug("Calling on_pipeline_status()")
  common_password = getpass.getpass('Enter the password:')
  inventory_file = cli_args.get("inventory_file", "")
  if is_valid_string(inventory_file):
    logger.debug("Pipeline status selected for " + inventory_file)
    try:
      inventory_data = load_inventory(file_name=inventory_file)
      ei_lm.execute_pipelines(inventory_data, operation=ei_lm.STATUS, device_pwd=common_password)
    except Exception as ex:
      print(ex)
  else:
    print("\nPlease provide a valid pipeline inventory file option\n")
    logger.error("Invalid : pipeline inventory file options :" + str(inventory_file))
    parser.print_help()

def on_agent_status(cli_args, parser):
  print("on_agent_status", cli_args)

def on_agent_reset(cli_args, parser):
  print("on_agent_reset", cli_args)

def on_user_change_pwd(cli_args, parser):
  logger.debug("Calling on_user_change_pwd()")
  old_password = getpass.getpass('Enter the old password:')
  inventory_file = cli_args.get("inventory_file", "")
  new_password = getpass.getpass('Enter the new password:')
  if is_valid_string(inventory_file):
    logger.debug("Change password selected for " + inventory_file)
    try:
      inventory_data = load_inventory(file_name=inventory_file)
      ei_lm.execute_pipelines(inventory_data, operation=ei_lm.CHANGE_PWD, device_pwd=old_password, new_password=new_password)
    except Exception as ex:
      print(ex)
  else:
    print("\nPlease provide a valid pipeline inventory file option\n")
    logger.error("Invalid : pipeline inventory file options :" + str(inventory_file))
    parser.print_help()

def load_inventory(file_name):
  # Check EI_CLI_HOME env is set or not
  if os.getenv(EI_CLI_HOME) is None:
    raise Exception("EI_CLI_HOME env variable is not set")
  # Check if the file exists
  file_path = os.path.join(os.getenv(EI_CLI_HOME), CONFIG_DIR, file_name)
  if not os.path.exists(file_path):
    logger.error("Inventory file does not exist at path '{}'".format(file_path))
    raise Exception("Inventory file does not exist at path '{}'".format(file_path))
  # Load the inventory file and return the yaml object in dict
  try:
    logger.debug("Loading inventory file from path '{}'".format(file_path))
    with open(file_path) as f:
      inventory_data = yaml.safe_load(f.read())
      logger.debug(inventory_data)
      return inventory_data
  except Exception as e:
    logger.error("Failed to load/parse '{}': {}".format(file_path, e))
    raise Exception("Failed to load/parse '{}': {}".format(file_path, e))
  return None

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='...')
    p.add_argument('--argument', required=False)
    p.add_argument('-a', required='--argument' in sys.argv)  # only required if --argument is given
    p.add_argument('-b', required='--argument' in sys.argv)  # only required if --argument is given
    print(p.parse_args())
