# Analysis Example
# Creating devices using dashboard
#
# Using an Input Widget in the dashboard, you will be able to create devices in your account.
# You can get the dashboard template to use here: https://admin.tago.io/template/6143555a314cef001871ec78
# Use a dummy HTTPs device with the dashboard.
#
# Environment Variables
# In order to use this analysis, you must setup the Environment Variable table.
#   account_token: Your account token. Check bellow how to get this.
#
# Steps to generate an account_token:
# 1 - Enter the following link: https://admin.tago.io/account/
# 2 - Select your Profile.
# 3 - Enter Tokens tab.
# 4 - Generate a new Token with Expires Never.
# 5 - Press the Copy Button and place at the Environment Variables tab of this analysis.

from tago import Utils, Analysis, Device, Account

def startAnalysis(context, scope):
  if not scope:
    return context.log("The analysis must be triggered by a widget.")

  # reads the value of account_token from the environment variable
  account_token = list(filter(lambda account_token: account_token['key'] == 'account_token', context.environment))
  account_token = account_token[0]['value']

  if not account_token:
    return context.log("Missing account_token Environment Variable.")

  # Instance the Account class
  account = Account(account_token)

  # Get the token of the settings device used in the dashboard, then instance the device class.
  # We will use this to send the Validation (feedback) to the dashboard.
  dashboard_dev_token = Utils.getTokenByName(account, scope[0]["device"])
  dashboard_device = Device(token=dashboard_dev_token)

  # Get the variables sent by the widget/dashboard.
  device_network = [obj for obj in scope if obj["variable"]  == "device_network"]
  device_connector = [obj for obj in scope if obj["variable"]  == "device_connector"]
  device_name = [obj for obj in scope if obj["variable"]  == "device_name"]
  device_eui = [obj for obj in scope if obj["variable"]  == "device_eui"]

  if not device_network or not device_network[0]["value"]:
    return context.log('Missing "device_network" in the data scope.')
  elif not device_connector or not device_connector[0]["value"]:
    return context.log('Missing "device_connector" in the data scope.')
  elif not device_eui or not device_eui[0]["value"]:
    return context.log('Missing "device_eui" in the data scope.')

  new_device = {
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

  result = account.devices.create(data=new_device)
  context.log(result)
  result = result["result"]

  # To add Configuration Parameters to the device:
  account.devices.paramSet(
    device_id=result["device_id"], data={ "key": "param_key", "value": "10", "sent": False }
  )

  # To add any data to the device that was just created:
  # const device = new Device({ token: result.token })
  # device.sendData({ variable: 'temperature', value: 17 })

  # Send feedback to the dashboard:
  dashboard_device.insert(
    data={"variable": "validation", "value": "Device succesfully created!", "metadata": {"type": "success" } }
  )
  context.log(f"Device succesfully created. ID: {result['device_id']}")


# The analysis token in only necessary to run the analysis outside TagoIO
Analysis('MY-ANALYSIS-TOKEN-HERE').init(startAnalysis)
