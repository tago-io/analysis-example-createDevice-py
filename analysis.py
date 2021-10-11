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

from tago import Analysis
from tago import Account
from tago import Utils
from tago import Device

# The function myAnalysis will run when you execute your analysis
def myAnalysis(context,scope):
  account_token = list(filter(lambda account_token: account_token['key'] == 'account_token', context.environment))
  account_token = account_token[0]['value']
  if not account_token:
   return context.log("Missing account_token Environment Variable.")
  # Instance the Account class
  my_account = Account(account_token)
  # Get the token of the settings device used in the dashboard, then instance the device class.
  # We will use this to send the Validation (feedback) to the dashboard.
  dashboard_dev_token  = Utils.getTokenByName(my_account,scope[0]["origin"])
  dashboard_device = Device(dashboard_dev_token)
  # Get the variables sent by the widget/dashboard.
  network_id = list(filter(lambda network_id: network_id['variable'] == 'device_network', scope))
  network_id = network_id[0]['value']
  connector_id  = list(filter(lambda connector_id : connector_id ['variable'] == 'device_connector', scope))
  connector_id = connector_id[0]['value']
  device_name  = list(filter(lambda device_name : device_name ['variable'] == 'device_name', scope))
  device_name = device_name[0]['value']
  device_eui   = list(filter(lambda device_eui  : device_eui  ['variable'] == 'device_eui', scope))
  device_eui = device_eui[0]['value']
  if not network_id:
    return context.log('Missing "device_network" in the data scope.')
  if not connector_id:
    return context.log('Missing "device_connector" in the data scope.')
  if not device_name:
    return context.log('Missing "device_name" in the data scope.')
  if not device_eui:
    return context.log('Missing "device_eui" in the data scope.')
  result = my_account.devices.create({
    'name': device_name,
    'serie_number': device_eui,
    'tags': [
      { 'key': 'type', 'value': 'sensor' },
      { 'key': 'device_eui', 'value': device_eui},
    ],
    'connector': connector_id,
    'network': network_id,
    'active': True,
  })
  if not result:
    dashboard_device.insert({ 'variable': 'validation', 'value': 'Error when creating the device', 'metadata': { 'color': 'red' } })
  my_account.devices.paramSet(result['result']['device_id'], { 'key': 'param_key', 'value': '10', 'sent': False })
  dashboard_device.insert({ 'variable': 'validation', 'value': 'Device succesfully created!', 'metadata': { 'type': 'success' } })
  context.log('Device succesfully created. ID:',result['result']['device_id'])
# The analysis token in only necessary to run the analysis outside TagoIO
Analysis('1fa28cb1-1ab3-4d91-b578-7f5d3dc631a9').init(myAnalysis)
