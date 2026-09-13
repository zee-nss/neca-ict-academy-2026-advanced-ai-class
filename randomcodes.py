import requests

response = requests.get('https://api.service.com/data',
                        headers = {'Authorization': 'Bearer KEY'},params={'date': '2025-01-15'})

if response.status_code == 200:
    data = response.json()
    print("Data recieved successfully")
else:
    print('Error:', response.status_code)