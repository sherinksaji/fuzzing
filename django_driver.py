import requests, json
from fuzzer import Fuzzer
import subprocess
import json

base_url = 'http://127.0.0.1:8000/datatb/product/'

# Define the endpoint URL
endpoint_url = 'add/'
# endpoint_url = 'delete/'


url = base_url + endpoint_url

def main():
    initial_input = ['bbbba', '111f', 99]
    for i in range(50):
            fuzzer = Fuzzer()
            output = fuzzer.mutator.mutate(initial_input)
            form_data = {
                'name': output[0],
                'info': output[1],
                'price': output[2]
            }
            headers = {
                'Cookie': 'csrftoken=5vvs6151ScRQGpdMlKAf8FAFERO67MmK; sessionid=c35o5m7xkymbjdtcu9k916f8jfj2f8x7', # Optional
            }

            try:
                print(json.dumps(form_data))
                # response = requests.post(url+str(i)+'/', headers=headers, data=json.dumps(form_data), )
                response = requests.post(url, headers=headers, data=json.dumps(form_data), )


                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    print("Request successful!")
                    db_return = check_db.fetch_products(info=fuzzed_inputs.get('info'), name=fuzzed_inputs.get('name'),
                    price = fuzzed_inputs.get('price'))
                    price = fuzzed_inputs.get('price')
                    # Process the response data as needed
                    print("Response:")
                    print(response.text)

                else:
                    print(f"Request failed with status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print("Request failed:", e)



            

if __name__ == "__main__":
    main()
