"""
Analysis Example
Creating devices using dashboard

Using an Input Widget in the dashboard, you will be able to create devices in your account.
You can get the dashboard template to use here: https://admin.tago.io/template/6143555a314cef001871ec78
Use a dummy HTTPs device with the dashboard.

Environment Variables
In order to use this analysis, you must setup the Environment Variable table.
  account_token: Your account token. Check bellow how to get this.

Steps to generate an account_token:
1 - Enter the following link: https://admin.tago.io/account/
2 - Select your Profile.
3 - Enter Tokens tab.
4 - Generate a new Token with Expires Never.
5 - Press the Copy Button and place at the Environment Variables tab of this analysis.
"""

from tagoio_sdk import Analysis, Device, Account
from tagoio_sdk.modules.Utils.getTokenByName import getTokenByName
from tagoio_sdk.modules.Account.Device_Type import DeviceCreateInfo


def add_configuration_parameter_to_device(account: Account, device_id: str) -> None:
    account.devices.paramSet(
        deviceID=device_id, configObj={ "key": "param_key", "value": "10", "sent": False }
    )


def send_feedback_to_dashboard(account: Account, device_id: str) -> None:
    dashboard_token = getTokenByName(account=account, deviceID=device_id)
    device = Device(params={"token":dashboard_token})

    # To add any data to the device that was just created:
    # device.sendData({ "variable": "temperature", value: 17 })

    device.sendData(
        data={"variable": "validation", "value": "Device successfully created!", "metadata": {"type": "success" } }
    )


def parse_new_device(scope: list[dict]) -> DeviceCreateInfo:
    # Get the variables sent by the widget/dashboard.
    device_network = [obj for obj in scope if obj["variable"]  == "device_network"]
    device_connector = [obj for obj in scope if obj["variable"]  == "device_connector"]
    device_name = [obj for obj in scope if obj["variable"]  == "device_name"]
    device_eui = [obj for obj in scope if obj["variable"]  == "device_eui"]

    if not device_network or not device_network[0]["value"]:
        raise TypeError('Missing "device_network" in the data scope.')
    elif not device_connector or not device_connector[0]["value"]:
        raise TypeError('Missing "device_connector" in the data scope.')
    elif not device_eui or not device_eui[0]["value"]:
        raise TypeError('Missing "device_eui" in the data scope.')

    return {
        "name": device_name[0]["value"],
        "serie_number": device_eui[0]["value"],
        "tags": [
            # You can add custom tags here.
            { "key": "type", "value": "sensor" },
            { "key": "device_eui", "value": device_eui[0]["value"] },
        ],
        "connector": device_connector[0]["value"],
        "network": device_network[0]["value"],
        "active": True,
        "type": "immutable",
        "chunk_period": "month", # consider change
        "chunk_retention": 1, # consider change
    }


def start_analysis(context: list[dict], scope: list[dict]) -> None:
    if not scope:
        return print("The analysis must be triggered by a widget.")

    # reads the value of account_token from the environment variable
    account_token = list(filter(lambda account_token: account_token["key"] == "account_token", context.environment))
    account_token = account_token[0]["value"]

    if not account_token:
        return print("Missing account_token Environment Variable.")

    account = Account(params={"token": account_token})

    new_device = parse_new_device(scope=scope)

    result = account.devices.create(deviceObj=new_device)
    print(result)

    add_configuration_parameter_to_device(account=account, device_id=result["device_id"])

    send_feedback_to_dashboard(account=account, device_id=scope[0]["device"])

    print(f"Device successfully created. ID: {result['device_id']}")


# The analysis token in only necessary to run the analysis outside TagoIo
Analysis(params={"token": "MY-ANALYSIS-TOKEN-HERE"}).init(start_analysis)
