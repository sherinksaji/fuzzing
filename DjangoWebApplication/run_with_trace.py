import sys
import trace
import coverage
import trace
import subprocess
import time
import os
import signal
import random
import json
import requests
import multiprocessing

trace_ls = []


def my_trace_filter(frame, event, arg_unused):
    filename = frame.f_globals["__file__"]
    if "/usr/lib/python3" in filename or "site-packages" in filename:
        # Skip standard library and installed packages
        return None
    else:
        # Print or log the trace info as desired
        # print(f"Tracing {filename}, event: {event}")
        trace_tuple = (filename, event)
        trace_ls.append(trace_tuple)

    return my_trace_filter


# Function to start the Django server with tracing
def run_django_server_with_trace():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "your_project.settings"
    )  # Adjust as necessary
    from django.core.management import execute_from_command_line

    # Set up tracing
    tracer = trace.Trace(tracefunc=my_trace_filter, trace=1)

    # This part is tricky; you're directly invoking the management command equivalent to 'runserver'
    # You might need to adjust arguments based on your Django project's needs
    def start_server():
        execute_from_command_line(["manage.py", "runserver"])

    # Start tracing and run the Django server
    tracer.runfunc(start_server)


# Start the Django server with tracing in a separate process
server_process = multiprocessing.Process(target=run_django_server_with_trace)
server_process.start()


print("Server started...")

# Sleep for a few seconds to ensure the server starts up
time.sleep(60)

# Your testing logic here, e.g., making HTTP requests to your Django app
# It's important that your testing script makes requests to the server
# to cover the application's code paths.

# Example: Placeholder for your testing logic
# perform_tests()
base_url = "http://127.0.0.1:8000/datatb/product/"

endpoint_url = "add/"

url = base_url + endpoint_url

random_name = "".join(
    random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10)
)
random_info = "".join(
    random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=10)
)
random_price = str(random.randint(1, 100))

form_data = {"name": random_name, "info": random_info, "price": random_price}

headers = {
    "Cookie": "csrftoken=5vvs6151ScRQGpdMlKAf8FAFERO67MmK; sessionid=c35o5m7xkymbjdtcu9k916f8jfj2f8x7",  # Optional
}

try:
    print(json.dumps(form_data))
    response = requests.post(url, headers=headers, data=json.dumps(form_data))

    if response.status_code == 200:
        print("Request successful!")
        print("Response:")
        print(response.text)

    else:
        print(f"Request failed with status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print("Request failed:", e)

# Terminate the server process
server_process.terminate()
server_process.join()

# Access or print your trace results
print(trace_ls)
print("Server terminated.")
