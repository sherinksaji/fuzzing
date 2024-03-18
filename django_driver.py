import requests, json
from fuzzer import Fuzzer

base_url = 'http://127.0.0.1:8000/datatb/product/'

# Define the endpoint URL
endpoint_url = 'delete/'

url = base_url + endpoint_url

def main():
    for i in range(100):
            try:
                fuzzer = Fuzzer(40)
                a = fuzzer.generate_random_str()
                mutated_a = fuzzer.mutate_str(a)
                fuzzer2 = Fuzzer(4)
                mutated_info = fuzzer.mutate_str(fuzzer2.generate_random_str())
                form_data = {
                    'name': mutated_a,
                    'info': mutated_info,
                    'price': "12"
                }
                headers = {
                    'Cookie': 'csrftoken=5vvs6151ScRQGpdMlKAf8FAFERO67MmK; sessionid=c35o5m7xkymbjdtcu9k916f8jfj2f8x7', # Optional
                }

                try:
                    print(json.dumps(form_data))
                    response = requests.post(url+str(i)+'/', headers=headers, data=json.dumps(form_data), )

                    # Check if the request was successful (status code 200)
                    if response.status_code == 200:
                        print("Request successful!")
                        # Process the response data as needed
                        print("Response:")
                        print(response.text)

                    else:
                        print(f"Request failed with status code: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print("Request failed:", e)

            except UnicodeDecodeError as e:
                continue

if __name__ == "__main__":
    main()