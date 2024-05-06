import subprocess
from django.shortcuts import render
from django.http import JsonResponse

def get_device_names():
    # Run the adb devices command to get the list of attached devices
    process = subprocess.Popen(['adb', 'devices'], stdout=subprocess.PIPE)
    output, _ = process.communicate()

    # Decode the output and split it into lines
    output_lines = output.decode('utf-8').split('\n')

    # Initialize a list to store device IDs
    device_ids = []

    # Iterate over the output lines starting from the second line
    for line in output_lines[1:]:
        # Split each line to extract device ID
        parts = line.split()
        if len(parts) >= 1:
            device_id = parts[0]  # The device ID is the first part of the line
            device_ids.append(device_id)

    return device_ids

def get_device_details():
    device_ids = get_device_names()
    device_details_list = []

    # Iterate over each device ID
    for device_id in device_ids:
        # Get Wi-Fi information for the device
        device_details = get_device_info(device_id)
        # Append device details to the list
        device_details_list.append(device_details)

    return device_details_list

def get_device_info(device_id):
    # Initialize a dictionary to store device details
    device_details = {'device_id': device_id}

    # Execute adb shell command to get product model
    process_model = subprocess.Popen(['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    model_output, _ = process_model.communicate()
    device_details['Product_Model'] = model_output.decode('utf-8').strip()

    # Execute adb shell command to get build version
    process_version = subprocess.Popen(['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    version_output, _ = process_version.communicate()
    device_details['Build_Version'] = version_output.decode('utf-8').strip()

    # Execute adb shell command to get product manufacturer name
    process_manufacturer = subprocess.Popen(['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.manufacturer'],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    manufacturer_output, _ = process_manufacturer.communicate()
    device_details['Manufacturer'] = manufacturer_output.decode('utf-8').strip()

    # Get Bluetooth status
    bluetooth_status = subprocess.check_output(['adb', '-s', device_id, 'shell', 'settings', 'get', 'global', 'bluetooth_on']).decode('utf-8').strip()
    device_details['Bluetooth_Status'] = True if bluetooth_status == '1' else False

    # Get Wi-Fi status
    wifi_status = subprocess.check_output(['adb', '-s', device_id, 'shell', 'settings', 'get', 'global', 'wifi_on']).decode('utf-8').strip()
    device_details['Wifi_Status'] = True if wifi_status == '1' else False

    return device_details


def get_bluetooth_status(device_id):
    try:
        output = subprocess.check_output(['adb', '-s', device_id, 'shell', 'settings', 'get', 'global', 'bluetooth_on'])
        return int(output.decode('utf-8').strip()) == 1
    except subprocess.CalledProcessError:
        # Error occurred, return None to indicate failure
        return None

def get_wifi_status(device_id):
    try:
        output = subprocess.check_output(['adb', '-s', device_id, 'shell', 'settings', 'get', 'global', 'wifi_on'])
        return int(output.decode('utf-8').strip()) == 1
    except subprocess.CalledProcessError:
        # Error occurred, return None to indicate failure
        return None

def toggle_bluetooth(request):
    device_id = request.GET.get('device_id')
    current_status = get_bluetooth_status(device_id)
    
    if current_status is None:
        message = 'Failed to get Bluetooth status'
    else:
        try:
            if current_status:
                subprocess.check_output(['adb', '-s', device_id, 'shell', 'svc', 'bluetooth', 'disable'])
                message = 'Bluetooth disabled successfully'
            else:
                subprocess.check_output(['adb', '-s', device_id, 'shell', 'svc', 'bluetooth', 'enable'])
                message = 'Bluetooth enabled successfully'
        except subprocess.CalledProcessError:
            message = 'Failed to toggle Bluetooth'
    
    return JsonResponse({'message': message})

def toggle_wifi(request):
    device_id = request.GET.get('device_id')
    current_status = get_wifi_status(device_id)
    
    if current_status is None:
        message = 'Failed to get Wi-Fi status'
    else:
        try:
            if current_status:
                subprocess.check_output(['adb', '-s', device_id, 'shell', 'svc', 'wifi', 'disable'])
                message = 'Wi-Fi disabled successfully'
            else:
                subprocess.check_output(['adb', '-s', device_id, 'shell', 'svc', 'wifi', 'enable'])
                message = 'Wi-Fi enabled successfully'
        except subprocess.CalledProcessError:
            message = 'Failed to toggle Wi-Fi'
    
    return JsonResponse({'message': message})


def home(request):
    device_details_list = get_device_details()
    return render(request, 'home.html', {'device_list': device_details_list})
