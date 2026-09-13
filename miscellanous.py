# # # # Run this, let it crash, screenshot the red error in the terminal
# # # open('this_file_does_not_exist.txt')

# # import requests

# # # Test the weather API
# # url = "https://api.open-meteo.com/v1/forecast"
# # params = {"latitude": 6.5244, "longitude": 3.3792, "current_weather": True}
# # response = requests.get(url, params=params)
# # print("Weather API status:", response.status_code)
# # if response.status_code == 200:
# #     print("Weather API works!")

# # # Test the exchange rate API
# # url2 = "https://open.er-api.com/v6/latest/USD"
# # response2 = requests.get(url2)
# # print("Exchange API status:", response2.status_code)
# # if response2.status_code == 200:
# #     print("Exchange API works!")

# # # Test the random user API
# # url3 = "https://randomuser.me/api/?results=5"
# # response3 = requests.get(url3)
# # print("Random User API status:", response3.status_code)
# # if response3.status_code == 200:
# #     print("Random User API works!")

# import requests

# # Test the quotes site
# response = requests.get("http://quotes.toscrape.com/")
# print("Quotes site status:", response.status_code)

# # Test the books site
# response2 = requests.get("http://books.toscrape.com/")
# print("Books site status:", response2.status_code)


#deployment id AKfycbxqgXDHADT8iMFDDgXCIa4KFqZkrP9GSjLQlwr4uf9B-nVT6WbOSelVvIiSL_YFCPwi
#web app:https://script.google.com/macros/s/AKfycbxqgXDHADT8iMFDDgXCIa4KFqZkrP9GSjLQlwr4uf9B-nVT6WbOSelVvIiSL_YFCPwi/exec