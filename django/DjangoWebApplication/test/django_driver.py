import threading

import requests
from fuzzer import Fuzzer
import json
import os

import check_db

base_url = 'http://127.0.0.1:8000/datatb/product/'

# Define the endpoint URL
endpoint_url = 'add/'
# endpoint_url = 'delete/'


url = base_url + endpoint_url

def read_last_line(filename):
    with open(f'../{filename}', 'rb') as file:
        file.seek(0, os.SEEK_END)  # Go to the end of the file
        end_byte = file.tell()
        while file.tell() > 0:
            file.seek(-2, os.SEEK_CUR)  # Move backwards 2 bytes
            if file.read(1) == b'\n':  # If it's a newline character
                return file.readline().decode().strip()
            # If we are at the start of the file, return the first line
            if file.tell() == 1:
                file.seek(0)
                return file.readline().decode().strip()
        # If the file is empty, return an empty string
        file.seek(0)
        if end_byte == 0:
            return ""
        else:  # If the file has no newline characters (single line)
            return file.readline().decode().strip()

def handle_response():
        last_line = read_last_line("coverage.txt")
        path = last_line.split(",")[0]
        return path

def main():
    initial_input = ['aaaaaaa', '0000', 6666]
    fuzzer = Fuzzer(initial_input)

    seed_count = 0

    while True:

        energy = fuzzer.assignEnergy()
        seed_input = fuzzer.chooseNext()

        for i in range(energy):
            mutated_input = fuzzer.mutate(seed_input)
            form_data = {
                'name': mutated_input[0],
                'info': mutated_input[1],
                'price': mutated_input[2]
            }
            headers = {
                'Cookie': 'csrftoken=5vvs6151ScRQGpdMlKAf8FAFERO67MmK; sessionid=c35o5m7xkymbjdtcu9k916f8jfj2f8x7', # Optional
            }

            try:
                print(json.dumps(form_data))
                # response = requests.post(url+str(i)+'/', headers=headers, data=json.dumps(form_data), )
                response = requests.post(url, headers=headers, data=json.dumps(form_data),)

                db_return = check_db.fetch_products(info=form_data.get('info'), name=form_data.get('name'),
                                                    price = form_data.get('price'))
                # if db_return !valid
                #     fuzzer.updateFailQ(mutated_input)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    print("Request successful!")
                    print(db_return)
                    path = handle_response()
                    print('============',path, fuzzer.is_interesting(path, mutated_input), seed_count,'============')
                    fuzzer.is_interesting(path, mutated_input)
                    # Process the response data as needed
                    print("Response:")
                    print(response.text)

                    if (len(db_return) == 2):
                        with open('fail_input.json','a') as file:
                            file.write('logical bug: '+ str(form_data)+'\n')


                else:
                    print(f"Request failed with status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print("Request failed:", e)


        seed_count+=1



            

if __name__ == "__main__":
    main()
