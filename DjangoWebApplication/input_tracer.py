# input_tracer.py

import sys
import trace
from django.core.management.base import BaseCommand

import subprocess
import time
import os
import signal
import random
import json
import requests


class Command(BaseCommand):
    help = "Trace the path taken by input in a Django application"

    def handle(self, *args, **options):
        tracer = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix], trace=0, count=1)
        with tracer:
            # Perform actions that trigger input in your Django application
            # For example, make HTTP requests, call views, etc.
            # Start Django development server as a subprocess
            server_process = subprocess.Popen(["python", "manage.py", "runserver"])

            print("Server started...")

            # Sleep for a few seconds to ensure the server starts up
            time.sleep(5)

            # Your testing logic here, e.g., making HTTP requests to your Django app
            # It's important that your testing script makes requests to the server
            # to cover the application's code paths.

            # Example: Placeholder for your testing logic
            # perform_tests()
            base_url = "http://127.0.0.1:8000/datatb/product/"

            endpoint_url = "add/"

            url = base_url + endpoint_url

            random_name = "".join(
                random.choices(
                    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10
                )
            )
            random_info = "".join(
                random.choices(
                    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10
                )
            )
            random_price = str(random.randint(1, 100))

            form_data = {
                "name": random_name,
                "info": random_info,
                "price": random_price,
            }

            headers = {
                "Cookie": "csrftoken=5vvs6151ScRQGpdMlKAf8FAFERO67MmK; sessionid=c35o5m7xkymbjdtcu9k916f8jfj2f8x7",  # Optional
            }

            try:
                print(json.dumps(form_data))
                response = requests.post(
                    url, headers=headers, data=json.dumps(form_data)
                )

                if response.status_code == 200:
                    print("Request successful!")
                    print("Response:")
                    print(response.text)

                else:
                    print(f"Request failed with status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print("Request failed:", e)

            # Stop the server after tests
            server_process.terminate()
            server_process.wait()
