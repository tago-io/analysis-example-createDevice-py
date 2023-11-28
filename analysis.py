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
from datetime import datetime, timedelta

from tagoio_sdk import Analysis, Device, Resources
from tagoio_sdk.modules.Account.Device_Type import DeviceCreateInfo
from typing import Optional, TypedDict, Literal

validation_type = Literal["success", "danger", "warning"]


class IValidateOptions(TypedDict):
    show_markdown: Optional[bool]
    user_id: Optional[str]


def initialize_validation(validation_variable:str, device_id: str, opts: IValidateOptions = None):
    tokens = Resources().devices.tokenList(deviceID=device_id)
    device = Device(params={"token":tokens[0]["token"]})

    if opts is None:
        opts = {}
    i = 0

    def _(message: str, type: validation_type = "success"):
        nonlocal i
        if not message or not type:
            raise ValueError("Missing message or type")

        i += 1

        # Clean validation old entries
        device.deleteData({
            'variables': validation_variable,
            'qty': 999,
            'end_date': (datetime.utcnow() - timedelta(minutes=1)).isoformat()
        })

        validation_types = ["success", "danger", "warning"]

        # Insert the new entry
        device.sendData({
            'variable': validation_variable,
            'value': message,
            'time': (datetime.utcnow() + timedelta(milliseconds=i * 200)).isoformat(),
            'metadata': {
                'type': type if type in validation_types else None,
                'color': type if type not in validation_types else None,
                'show_markdown': bool(opts.get('show_markdown')),
                'user_id': opts.get('user_id')
            }
        })

        return message

    return _


def add_configuration_parameter_to_device(device_id: str) -> None:
    Resources().devices.paramSet(
        deviceID=device_id, configObj={ "key": "param_key", "value": "10", "sent": False }
    )


def parse_new_device(scope: list[dict]) -> DeviceCreateInfo:
    # Get the variables sent by the widget/dashboard.
    device_network = next(filter(lambda payload: payload["variable"] == "device_network", scope), None)
    device_connector = next(filter(lambda payload: payload["variable"] == "device_connector", scope), None)
    device_name = next(filter(lambda payload: payload["variable"] == "device_name", scope), None)
    device_eui = next(filter(lambda payload: payload["variable"] == "device_eui", scope), None)

    if not device_network or not device_network.get("value"):
        raise TypeError('Missing "device_network" in the data scope.')
    elif not device_connector or not device_connector.get("value"):
        raise TypeError('Missing "device_connector" in the data scope.')
    elif not device_name or not device_name.get("value"):
        raise TypeError('Missing "device_name" in the data scope.')
    elif not device_eui or not device_eui.get("value"):
        raise TypeError('Missing "device_eui" in the data scope.')

    return {
        "name": device_name["value"],
        "serie_number": device_eui["value"],
        "tags": [
            # You can add custom tags here.
            {"key": "type", "value": "sensor"},
            {"key": "device_eui", "value": device_eui["value"]},
        ],
        "connector": device_connector["value"],
        "network": device_network["value"],
        "active": True,
        "type": "immutable",
        "chunk_period": "month",  # consider change
        "chunk_retention": 1,  # consider change
    }


def start_analysis(context: list[dict], scope: list[dict]) -> None:
    if not scope:
        return print("The analysis must be triggered by a widget.")

    new_device = parse_new_device(scope=scope)
    settings_id = scope[0]["device"]

    validate = initialize_validation("validation", settings_id)
    validate("Creating device...", "warning")

    try:
        result = Resources().devices.create(deviceObj=new_device)
    except Exception as error:
        return validate(error, "danger")

    add_configuration_parameter_to_device(device_id=result["device_id"])

    validate("Device created successfully!", "success")


# The analysis token in only necessary to run the analysis outside TagoIO
Analysis.use(start_analysis, params={"token": "MY-ANALYSIS-TOKEN-HERE"})
