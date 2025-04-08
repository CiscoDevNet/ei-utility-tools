# EI Utility Tools

This repo contains tools related to EI Local Manager 

## EI Local Manager CLI Tool (eilm-cli)

### To build the package
```bash
cd ei-utility-tools
python3 setup.py sdist bdist_wheel
```

### To install the package
```bash
cd ei-utility-tools/dist
pip install eilm-cli-1.1.0.tar.gz
```

### Initialize and configure eilm-cli 

#### Set the Environment Variable EI_CLI_HOME
Create a directory (for example, “eilm-cli” under home folder) which we want to use as EI_CLI_HOME and set the path to environment variable EI_CLI_HOME
```commandline
export EI_CLI_HOME=<path_to_eilm_home_dir>
```

Example:
```commandline
export EI_CLI_HOME=/home/user/eilm-cli
```


#### For Windows PowerShell

```commandline
$env:EI_CLI_HOME="<path_to_eilm_home_dir>"
```
Example:
```commandline
$env:EI_CLI_HOME="C:\Users\Administrator\eilm-cli"
``` 
To get the variable value 
```commandline
PS C:\Users\Administrator>  $env:EI_CLI_HOME
C:\Users\Administrator\eilm-cli
PS C:\Users\Administrator>
```

Note: (Ensure the path is always enclosed in double quotes; otherwise, it will throw an error.)

#### For Windows CMD

>set EI_CLI_HOME="<path_to_eilm_home_dir>"

Example:
> set EI_CLI_HOME="C:\Users\Administrator\eilm-cli" 

OR
 
> set EI_CLI_HOME=C:\Users\Administrator\eilm-cli

```
C:\Users\Administrator> echo %EI_CLI_HOME%
"C:\Users\Administrator\eilm-cli"
C:\Users\Administrator>
```

### Initialize Configurations

Run the initialization command to generate a configuration folder and sample configuration files

```
~/eilm-cli$ eilm-cli init
EI CLI env successfully initialized at '/Users/EI/eilm-cli'
```
This will create a configs folder under EI_CLI_HOME folder with sample JSON configuration files inside the sample folder.
```
~/eilm-cli$ ls -ltr
total 2
drwxr-xr-x  3 root  root    96 Jan 11 15:45 configs
-rw-r--r--  1 root  root  1029 Jan 11 15:55 eilm-cli.log
```

```
~/EI/eilm-cli$ ls -ltr configs/sample 
total 4
-rw-r--r--  1 root  root   493 Jan 11 15:43 data_logic_1.json
-rw-r--r--  1 root  root  1359 Jan 11 15:43 data_source_1.json
-rw-r--r--  1 root  root   968 Jan 11 15:43 data_target_1.json
-rw-r--r--  1 root  root   119 Jan 11 15:43 data_vars_1.json

```
Check if the eilm-cli command is working using help 
```
~/eilm-cli$ eilm-cli --help
usage: eilm-cli [-h] {init,user,agent,pipeline} ...

EI Local Manager CLI Orchestrator [Version 1.1.0]

positional arguments:
  {init,user,agent,pipeline}
                        options
    init                initialize eilm-cli environment
    user                user operations (change-password)
    agent               agent operations (status, reset)
    pipeline            pipeline operations (deploy, undeploy, status)

options:
  -h, --help            show this help message and exit
```

### Create the Pipeline Inventory File
#### Step 1
The user needs to create a pipeline inventory file under the configs folder. This file will contain all the required configuration (like device info, configuration, etc) for the pipeline to be deployed. 
Before creating the pipeline inventory file, the user also needs to create few configuration files which will be used in the pipeline-inventory file described in Step 2

> cd <ei_cli_home>/configs

#### Step 2 
Below are the required individual configuration files for the pipeline (data_source, data_logic, data_target, and data_variables). Please refer to the sample configuration files, which will be used in the pipeline inventory file

pipeline_template : This is a JSON file which contains the data source, destination, pipeline configuration. actually this could be a file exported from EI that can be used as template to deploy on other EI agents.

```
{
  "name": "pipeline-template-datalogic",
  "data": {
    "dataSources": {
      "mqtt1": {
        "type": "MQTT",
        "assetId": "1234",
        "dataSourceConfiguration": {
          "port": null,
          "secure": false,
          "useWebSockets": false,
          "clientId": "test",
          "assetId": "1234",
          "name": "endpoint_1883",
          "endpoints": [
            {
              "clientId": "test",
              "port": "1883",
              "credentials": [
                {
                  "username": "gogopals@cisco.com",
                  "password": "10000:KusMo5cIWx/tkKNKeeDfWg==:+z5Pjl3JkNgqLje+Hl+xDnhG7jEL04/F0LyAyIY1KO3avuZn8n8k/+2xchX9s6ty/W4azkJbb1nnflUaeh4YCg=="
                }
              ],
              "name": "endpoint_1883",
              "metrics": {
                "test": {
                  "name": "test",
                  "label": "test",
                  "datatype": "String",
                  "topic": "test_topic"
                },
                "test2": {
                  "name": "test2",
                  "label": "test2",
                  "datatype": "String",
                  "topic": "test_topic2"
                }
              },
              "secure": false,
              "privateKey": null,
              "serverCertificate": null
            }
          ]
        },
        "fields": [
          {
            "type": "subscription",
            "key": "test",
            "source": "/endpoints/endpoint_1883/test/test_topic"
          },
          {
            "type": "subscription",
            "key": "test2",
            "source": "/endpoints/endpoint_1883/test/test_topic2"
          },
          {
            "type": "customAttribute",
            "key": "custom1",
            "value": "test_custome_value"
          }
        ]
      },
      "mqtt2": {
        "type": "MQTT",
        "assetId": "4567",
        "dataSourceConfiguration": {
          "port": null,
          "secure": false,
          "useWebSockets": false,
          "clientId": "gg-mclient-2",
          "assetId": "4567",
          "name": "endpoint_1883",
          "endpoints": [
            {
              "clientId": "gg-mclient-2",
              "port": "1883",
              "credentials": [
                {
                  "username": "gogopals@cisco.com",
                  "password": "10000:AZhjbaVaNp7imy7ZYvVRRQ==:d/pMLrrCfUKuJbTbKUgplumM0THVvJjZD5s6Mw0nhx4z+vptlTp4glkV5j57l7p1tIJFDpOq/V9q+nU5jPXKzQ=="
                }
              ],
              "name": "endpoint_1883",
              "metrics": {
                "test2": {
                  "name": "test2",
                  "label": "test",
                  "datatype": "String",
                  "topic": "test_topic2"
                }
              },
              "secure": false,
              "privateKey": null,
              "serverCertificate": null
            }
          ]
        },
        "fields": [
          {
            "type": "subscription",
            "key": "test2",
            "source": "/endpoints/endpoint_1883/gg-mclient-2/test_topic2"
          }
        ]
      }
    },
    "dataTarget": {
      "type": "MQTT",
      "dataTargetConfiguration": {
        "connectors": [
          {
            "host": "$TARGET_HOST",
            "port": 1884,
            "secure": false,
            "verifyPeer": false,
            "mqttQoS": 1,
            "clientId": "12344567_3fcbaece-ce1b-428b-995e-2b0319710180",
            "cleanSession": true,
            "username": "gogopals@cisco.com",
            "password": "Welcome@12345",
            "publish": {
              "resultPath": {
                "mqttRetain": true,
                "mqttQos": 1,
                "mqttTopic": "cisco/edge-intelligence/telemetry/12344567"
              }
            }
          }
        ]
      }
    },
    "outputModel": {},
    "scriptedDataLogic": {
      "enableCloudCommands": false,
      "parameters": {
        "INVOKE_ON_NEW_DATA": null
      },
      "productive": true,
      "script": "\u001bbytes:LyoqIFRoaXMgaXMgdGhlIG1hbmRhdG9yeSBmdW5jdGlvbiB0aGF0IGVhY2ggRUkgZGF0YSBsb2dpYyBtdXN0IGltcGxlbWVudAogKiAgU3RhcnQgb2YgRUkgRGF0YSBMb2dpYyovCi8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8KCmZ1bmN0aW9uIG9uX3VwZGF0ZSgpIHsKICAKICBwdWJsaXNoKCJvdXRwdXQiLCAidGVzdCIpOwp9CgovKipFbmQgb2YgRURNIGRhdGEgbG9naWMgKi8KCmZ1bmN0aW9uIG9uX3RpbWVfdHJpZ2dlcigpIHsKICBsb2dnZXIuaW5mbygib25fdGltZV90cmlnZ2VyKysrKyB0aW1lc3RhbXAgPSAiICsgbmV3IERhdGUoKSk7IAogcHVibGlzaCgib3V0cHV0IiwgInRlc3QiKTsKfQo=",
      "invokeEvery": 1000
    }
  }
}
```

data_source : This is a JSON file which contains the data source configuration part of the data pipeline

```
{
  "dataSources": {
    "mqtt1": {
      "type": "MQTT",
      "assetId": "1234",
      "dataSourceConfiguration": {
        "port": null,
        "secure": false,
        "useWebSockets": false,
        "clientId": "test",
        "assetId": "1234",
        "name": "endpoint_1883",
        "endpoints": [
          {
            "clientId": "test",
            "port": "1883",
            "credentials": [
              {
                "username": "test_user@cisco.com",
                "password": "Welcome@12345"
              }
            ],
            "name": "endpoint_1883",
            "metrics": {
              "test": {
                "name": "test",
                "label": "test",
                "datatype": "String",
                "topic": "test_topic"
              },
              "test2": {
                "name": "test2",
                "label": "test2",
                "datatype": "String",
                "topic": "test_topic2"
              }
            },
            "secure": false,
            "privateKey": null,
            "serverCertificate": null
          }
        ]
      },
      "fields": [
        {
          "type": "subscription",
          "key": "test",
          "source": "/endpoints/endpoint_1883/test/test_topic"
        },
        {
          "type": "subscription",
          "key": "test2",
          "source": "/endpoints/endpoint_1883/test/test_topic2"
        },
        {
          "type": "customAttribute",
          "key": "custom1",
          "value": "test_custome_value"
        }
      ]
    },
    "mqtt2": {
      "type": "MQTT",
      "assetId": "4567",
      "dataSourceConfiguration": {
        "port": null,
        "secure": false,
        "useWebSockets": false,
        "clientId": "gg-mclient-2",
        "assetId": "4567",
        "name": "endpoint_1883",
        "endpoints": [
          {
            "clientId": "gg-mclient-2",
            "port": "1883",
            "credentials": [
              {
                "username": "test_user@cisco.com",
                "password": "Welcome@12345"
              }
            ],
            "name": "endpoint_1883",
            "metrics": {
              "test2": {
                "name": "test2",
                "label": "test",
                "datatype": "String",
                "topic": "test_topic2"
              }
            },
            "secure": false,
            "privateKey": null,
            "serverCertificate": null
          }
        ]
      },
      "fields": [
        {
          "type": "subscription",
          "key": "test2",
          "source": "/endpoints/endpoint_1883/gg-mclient-2/test_topic2"
        }
      ]
    }
  }
}
```

data_logic : This is a JSON file which contains the data logic configuration part of the data pipeline (This also contains data rule configurations)

```
{
  "scriptedDataLogic": {
    "enableCloudCommands": false,
    "parameters": {
      "INVOKE_ON_NEW_DATA": null
    },
    "productive": true,
    "script": "\u001bbytes:LyoqIFRoaXMgaXMgdGhlIG1hbmRhdG9yeSBmdW5jdGlvbiB0aGF0IGVhY2ggRUkgZGF0YSBsb2dpYyBtdXN0IGltcGxlbWVudAogKiAgU3RhcnQgb2YgRUkgRGF0YSBMb2dpYyovCi8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8KCmZ1bmN0aW9uIG9uX3VwZGF0ZSgpIHsKICAKICBwdWJsaXNoKCJvdXRwdXQiLCAidGVzdCIpOwp9CgovKipFbmQgb2YgRURNIGRhdGEgbG9naWMgKi8KCmZ1bmN0aW9uIG9uX3RpbWVfdHJpZ2dlcigpIHsKICBsb2dnZXIuaW5mbygib25fdGltZV90cmlnZ2VyKysrKyB0aW1lc3RhbXAgPSAiICsgbmV3IERhdGUoKSk7IAogcHVibGlzaCgib3V0cHV0IiwgInRlc3QiKTsKfQo=",
    "invokeEvery": "$INVOKE_INTERVAL"
  }
}
```

data_target : This is a JSON file which contains the data target configuration part of the data pipeline. This also contains output model configurations.
```
{
  "dataTarget": {
    "type": "MQTT",
    "dataTargetConfiguration": {
      "connectors": [
        {
          "host": "$TARGET_HOST",
          "port": 1884,
          "secure": false,
          "verifyPeer": false,
          "mqttQoS": "$MQTT_QOS",
          "clientId": "12344567_3fcbaece-ce1b-428b-995e-2b0319710180",
          "cleanSession": "$CLEAN_SESSION",
          "username": "test_user@cisco.com",
          "password": "Welcome@12345",
          "publish": {
            "resultPath": {
              "mqttRetain": true,
              "mqttQos": "$MQTT_QOS",
              "mqttTopic": "cisco/edge-intelligence/telemetry/12344567"
            }
          }
        }
      ]
    },
    "downSampling": {
      "update_interval": 1000
    }
  },
  "outputModel": {
    "test": {
      "addTimestamp": false,
      "emit": true,
      "targetPath": "test",
      "type": "STRING"
    },
    "test2": {
      "addTimestamp": false,
      "emit": true,
      "targetPath": "test2",
      "type": "STRING"
    }
  }
}
```

data_vars : This is a JSON file which contains the template variable configuration used in the data pipeline configuration

```
{
    "INVOKE_INTERVAL": 1000,
    "MQTT_QOS": 1,
    "CLEAN_SESSION": true,
    "TARGET_HOST": "test.mosquitto.org"
}
```
Note: The configuration provided above is a sample and may vary based on the specific pipeline configuration and use case. To obtain the exact configuration for a pipeline, please refer to the export pipeline functionality available in the Ei LM UI

#### Step 3
Create a pipeline configuration YAML file (inventory.yaml) using the data config files created in Step 2. 
This helps the user reuse the data configuration files in and for multiple pipeline deployments. 
To deploy / undeploy / status, the pipeline inventory file needs to be passed to the eilm-cli utility along with device credentials as shown below. (Refer Section 4 for more details on the commands supported.)
```
usage: eilm-cli pipeline deploy/undeploy/status [-f PIPELINE_INVENTORY_FILE]
example: eilm-cli pipeline deploy -f inventory.yaml
NOTE: This will prompt for the password. Prerequisite is that all the devices used in the inventory file should have same password.
```
The user can create as many number for pipeline inventory file he wants based on his requirements

Sample Inventory.yml file below
```
- DEVICE_IP: 10.1.1.100:8008
  PIPELINE_NAME: pipeline1
  PIPELINE_TEMPLATE: test_pipeline_template.json
  DATA_SOURCE_FILE: data_source_1.json
  DATA_LOGIC_FILE: data_logic_1.json
  DATA_TARGET_FILE: data_target_1.json
  DATA_VARIABLES_FILE: data_vars_1.json
- DEVICE_IP: 10.1.1.101:8008
  PIPELINE_NAME: pipeline2
  PIPELINE_TEMPLATE: test_pipeline_template.json
  DATA_SOURCE_FILE: data_source_2.json
  DATA_LOGIC_FILE: data_logic_2.json
  DATA_TARGET_FILE: data_target_3.json
  DATA_VARIABLES_FILE: data_vars_2.json
- DEVICE_IP: 10.1.1.102:8008
  PIPELINE_NAME: pipeline3
  PIPELINE_TEMPLATE: test_pipeline_template.json
  DATA_SOURCE_FILE: data_source_1.json
  DATA_LOGIC_FILE: data_logic_3.json
  DATA_TARGET_FILE: data_target_2.json
  DATA_VARIABLES_FILE: data_vars_1.json
```
Note: For single pipeline deployment on a single device, the inventory file will have only one entry.

### Using eilm-cli Utility
Note : Please note that the basic assumption is that the password for all the devices used in the pipeline-inventory.yaml file is the same. 

#### Change  Password
The user can in bulk change the password for all the devices configured in the inventory file using the following command. 

```
eilm-cli user change-pwd -f inventory.yaml

Above command will ask for old and new password

~/EI/demo$ eilm-cli user change-pwd -f test_inventory.yaml
Enter the old password:
Enter the new password:
[{'DEVICE_IP': '10.105.58.120:9001', 'PIPELINE_NAME': 'p001', 'DATA_SOURCE_FILE': 'test_data_source.json', 'DATA_LOGIC_FILE': 'test_data_logic.json', 'DATA_TARGET_FILE': 'test_data_target.json', 'DATA_VARIABLES_FILE': 'test_data_vars.json'}, {'DEVICE_IP': '10.105.58.120:9002', 'PIPELINE_NAME': 'p002', 'DATA_SOURCE_FILE': 'test_data_source.json', 'DATA_LOGIC_FILE': 'test_data_logic.json', 'DATA_TARGET_FILE': 'test_data_target.json', 'DATA_VARIABLES_FILE': 'test_data_vars.json'}, {'DEVICE_IP': '10.105.58.120:9003', 'PIPELINE_NAME': 'p003', 'DATA_SOURCE_FILE': 'test_data_source.json', 'DATA_LOGIC_FILE': 'test_data_logic.json', 'DATA_TARGET_FILE': 'test_data_target.json', 'DATA_VARIABLES_FILE': 'test_data_vars.json'}, {'DEVICE_IP': '10.105.58.120:9004', 'PIPELINE_NAME': 'p004', 'DATA_SOURCE_FILE': 'test_data_source.json', 'DATA_TARGET_FILE': 'test_data_target.json', 'DATA_VARIABLES_FILE': 'test_data_vars.json'}, {'DEVICE_IP': '10.105.58.120:9005', 'PIPELINE_NAME': 'p005', 'DATA_SOURCE_FILE': 'test_data_source.json', 'DATA_TARGET_FILE': 'test_data_target.json', 'DATA_VARIABLES_FILE': 'test_data_vars.json'}]
Started changing password on device 10.105.58.120:9001
Started changing password on device 10.105.58.120:9002
Started changing password on device 10.105.58.120:9003
Started changing password on device 10.105.58.120:9004
Started changing password on device 10.105.58.120:9005
Finished changing password on device 10.105.58.120:9001 Status: Success
Finished changing password on device 10.105.58.120:9003 Status: Success
Finished changing password on device 10.105.58.120:9004 Status: Success
Finished changing password on device 10.105.58.120:9005 Status: Success
Finished changing password on device 10.105.58.120:9002 Status: Success
```
This step generates a log file in the EI_CLI_HOME directory, e.g., change_pwd_<timestamp>.log.

#### Pipeline Operations
Below are the primary pipeline commands supported, and each command will ask for a password when executed. (Please note password should be same for all the devices used in the inventory file)

1. Deploy a Template:
```
(base) jhosalai@JHOSALAI-M-2YVX ei-cli-tool % eilm-cli pipeline deploy-template -f test_inventory.yml 
Enter the password:
[{'DEVICE_IP': '10.106.11.75:8008', 'PIPELINE_NAME': 'p002', 'PIPELINE_TEMPLATE': 'pipeline-template-datalogic_template.json', 'DATA_SOURCE_FILE': 'test_data_source.json', 'DATA_LOGIC_FILE': 'test_data_logic.json', 'DATA_TARGET_FILE': 'test_data_target.json', 'DATA_VARIABLES_FILE': 'test_data_vars.json'}]
$INVOKE_INTERVAL = [scriptedDataLogic][invokeEvery] = 1000
$MQTT_QOS = [dataTarget][dataTargetConfiguration][connectors][0][mqttQoS] = 1
$MQTT_QOS = [dataTarget][dataTargetConfiguration][connectors][0][publish][resultPath][mqttQos] = 1
$CLEAN_SESSION = [dataTarget][dataTargetConfiguration][connectors][0][cleanSession] = True
$TARGET_HOST = [dataTarget][dataTargetConfiguration][connectors][0][host] = 10.10.11.11
Started deploying pipeline p002 on device 10.106.11.75:8008
Finished deploying pipeline p002 on device 10.106.11.75:8008 Status: Success
```
2. Deploy a Pipeline:
```commandline
eilm-cli pipeline deploy -f inventory.yaml

Above command will ask for password

~/EI/demo$ eilm-cli pipeline deploy -f test_inventory.yaml
Enter the password:
[{'DEVICE_IP': '10.105.58.120:9001', 'PIPELINE_NAME': 'pipeline001', 'DATA_SOURCE_FILE': 'test_data_source_2.json', 'DATA_TARGET_FILE': 'test_data_target_2.json', 'DATA_VARIABLES_FILE': 'test_data_vars_2.json'}, {'DEVICE_IP': '10.105.58.120:9001', 'PIPELINE_NAME': 'pipeline002', 'DATA_SOURCE_FILE': 'test_data_source_1.json', 'DATA_LOGIC_FILE': 'test_data_logic_1.json', 'DATA_TARGET_FILE': 'test_data_target_1.json', 'DATA_VARIABLES_FILE': 'test_data_vars_1.json'}]
$MQTT_QOS = [dataTarget][dataTargetConfiguration][connectors][0][mqttQoS] = 1
$MQTT_QOS = [dataTarget][dataTargetConfiguration][connectors][0][publish][resultPath][mqttQos] = 1
$INVOKE_INTERVAL = [scriptedDataLogic][invokeEvery] = 1000
$MQTT_QOS = [dataTarget][dataTargetConfiguration][connectors][0][mqttQoS] = 1
$MQTT_QOS = [dataTarget][dataTargetConfiguration][connectors][0][publish][resultPath][mqttQos] = 1
$CLEAN_SESSION = [dataTarget][dataTargetConfiguration][connectors][0][cleanSession] = True
$TARGET_HOST = [dataTarget][dataTargetConfiguration][connectors][0][host] = 10.10.11.11
Started deploying pipeline pipeline001 on device 10.105.58.120:9001
Started deploying pipeline pipeline002 on device 10.105.58.120:9001
Finished deploying pipeline pipeline001 on device 10.105.58.120:9001 Status: Success
Finished deploying pipeline pipeline002 on device 10.105.58.120:9001 Status: Success
```
This step generates a log file in the EI_CLI_HOME directory, e.g., deploy_<timestamp>.log.
3. Undeploy a Pipeline
```commandline
eilm-cli pipeline undeploy -f inventory.yaml

Above command will ask for password

~/EI/demo$ eilm-cli pipeline undeploy -f test_inventory.yaml
Enter the password:
[{'DEVICE_IP': '10.105.58.120:9001', 'PIPELINE_NAME': 'pipeline001', 'DATA_SOURCE_FILE': 'test_data_source_2.json', 'DATA_TARGET_FILE': 'test_data_target_2.json', 'DATA_VARIABLES_FILE': 'test_data_vars_2.json'}, {'DEVICE_IP': '10.105.58.120:9001', 'PIPELINE_NAME': 'pipeline002', 'DATA_SOURCE_FILE': 'test_data_source_1.json', 'DATA_LOGIC_FILE': 'test_data_logic_1.json', 'DATA_TARGET_FILE': 'test_data_target_1.json', 'DATA_VARIABLES_FILE': 'test_data_vars_1.json'}]
Started un-deploying pipeline pipeline001 on device 10.105.58.120:9001
Started un-deploying pipeline pipeline002 on device 10.105.58.120:9001
Finished un-deploying pipeline pipeline001 on device 10.105.58.120:9001 Status: Success
Finished un-deploying pipeline pipeline002 on device 10.105.58.120:9001 Status: Success
```
This step generates a log file in the EI_CLI_HOME directory, e.g., status_<timestamp>.log.

4. Check Pipeline Status
```commandline
eilm-cli pipeline status -f inventory.yaml

Above command will ask for password

~/EI/demo$ eilm-cli pipeline status -f test_inventory.yaml
Enter the password:
[{'DEVICE_IP': '10.105.58.120:9001', 'PIPELINE_NAME': 'pipeline001', 'DATA_SOURCE_FILE': 'test_data_source_2.json', 'DATA_TARGET_FILE': 'test_data_target_2.json', 'DATA_VARIABLES_FILE': 'test_data_vars_2.json'}, {'DEVICE_IP': '10.105.58.120:9001', 'PIPELINE_NAME': 'pipeline002', 'DATA_SOURCE_FILE': 'test_data_source_1.json', 'DATA_LOGIC_FILE': 'test_data_logic_1.json', 'DATA_TARGET_FILE': 'test_data_target_1.json', 'DATA_VARIABLES_FILE': 'test_data_vars_1.json'}]
Started getting pipeline status for pipeline001 on device 10.105.58.120:9001
Started getting pipeline status for pipeline002 on device 10.105.58.120:9001
Finished getting pipeline status for pipeline002 on device 10.105.58.120:9001 Status: Stopped
Finished getting pipeline status for pipeline001 on device 10.105.58.120:9001 Status: Stopped
```
This step generates a log file in the EI_CLI_HOME directory, e.g., status_<timestamp>.log.
5. Logs Management
Log files for all operations are stored in the directory specified by the EI_CLI_HOME environment variable. Logs are named based on the operation and timestamp.

Examples:
- change_pwd_<timestamp>.log
- deploy_<timestamp>.log
- status_<timestamp>.log
- undeploy_<timestamp>.log

6. Troubleshooting

If you encounter issues:
Review the log files for error details. Verify the inventory.yaml file for accuracy.  Ensure all dependencies are installed and up to date.
For additional command details, refer to the help command 
> eilm-cli --help

## EI Scale Utility Script (ei-scale-utility.sh)

*This script is used to manage docker containers by providing options to start, stop or check the status of running EI Utility Containers. It allows you to specify the number of containers to start or stop and maps container ports dynamically based on user input.*

#### Features
* **Start Containers:** Start a specified number of containers using a custom image and environment variables.
* **Stop Containers:** Stop a specified number of running containers or stop all of them.
* **Check Status:** Display how many containers are currently running.
* **Port Mapping:** Automatically map container ports starting from a base external port.

#### Prerequisites
* Docker installed and running.
* Sufficient resources (memory, CPU) to run multiple containers.

#### Variables
|Variable Name	|Description |
|---------------|------------|
|SERVICE_NAME	|Descriptive name of the service (in this case, "EI Utility Containers").
|BUILD_ARGS	|Arguments passed when creating containers, including environment variables.
|IMAGE_NAME	|Docker image to use for creating containers (default: dockerhub-master.cisco.com/iot-darkphoenix-docker/ei-edge-testing:1.16.20).
|CONTAINER_NAME	|Base name of containers (e.g., ei-local-manager-1).
|EXT_PORT	|Base external port for mapping container ports to host ports (default: 9000).
|INT_PORT	|Internal port used within the containers (default: 8008).
|NUMBER_OF_CONTAINERS	|Number of containers to start or stop.
|CONTAINERS_RUNNING	|Number of containers that are currently running.
|NAME_OF_CONTAINERS_RUNNING	|Name of latest running containers.
|START_CONTAINERS_COUNT	|Name counter for the containers, used to uniquely name them when creating.

#### Usage
#### Start Containers
* To start a specified number of containers:

```bash
sh ei-scale-utility.sh start <number_of_containers>
```
For example, to start 5 containers:
```bash
sh ei-scale-utility.sh start 5
```
#### Stop Containers

* To stop a specified number of containers:

```bash
sh ei-scale-utility.sh stop <number_of_containers>
```
* For example, to stop 5 containers:

```bash
sh ei-scale-utility.sh stop 5
```
* To stop all running containers:

```bash
sh ei-scale-utility.sh stop all
```
#### Check Status
* To check the status of running containers:

```bash
sh ei-scale-utility.sh status
```
This will display the number of containers currently running.

#### Error Handling
If the required arguments are not provided for the start or stop commands, the script will display an error message like this:

```bash
========= Incomplete Arguments, Both arguments must be provided  =========
Exp:- sh ei-scale-utility.sh start 10|20
```

Similarly, when stopping containers, the script will ensure that the number of containers provided is not greater than the number of currently running containers.

#### Example
Starting 3 containers with the default configuration:

```bash
sh ei-scale-utility.sh start 3
```

Stopping 2 containers:

```bash
sh ei-scale-utility.sh stop 2
```

Checking the status of containers:

```bash
sh ei-scale-utility.sh status
```
#### Notes
* The script dynamically assigns external ports starting from the base port 9000. Each new container will map the next available port, incrementing by 1.
* Ensure you have sufficient resources to run the specified number of containers, especially when using a high number.
