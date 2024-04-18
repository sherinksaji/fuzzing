import subprocess
import threading
import queue
import time

# Global variable to control the flow based on tester output
tester_ready = threading.Event()


# Function to execute a command and handle its output
def execute_command(cmd, output_queue, prefix, trigger=None):
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            cleaned_output = output.strip()
            output_queue.put((prefix, cleaned_output))
            if trigger and "Waiting Advertisement from BLE Target" in cleaned_output:
                tester_ready.set()

    # Catch any error output
    errors = process.stderr.read()
    if errors:
        output_queue.put((prefix, errors.strip()))
    process.stdout.close()
    process.stderr.close()


# Function to display outputs from both processes
def display_outputs(output_queue):
    try:
        while True:
            if not output_queue.empty():
                prefix, output = output_queue.get()
                print(f"{prefix} {output}")
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped by user")


def main():
    output_queue = queue.Queue()

    # Define the commands to run
    cmd1 = ["python3", "-u", "run_ble_tester.py", "tcp-server:127.0.0.1:9000"]
    cmd2 = ["./zephyr.exe", "--bt-dev=127.0.0.1:9000"]

    # Start threads for each command
    thread1 = threading.Thread(
        target=execute_command, args=(cmd1, output_queue, "[Tester]", True), daemon=True
    )
    thread2 = threading.Thread(
        target=execute_command, args=(cmd2, output_queue, "[Zephyr]"), daemon=True
    )

    output_thread = threading.Thread(
        target=display_outputs, args=(output_queue,), daemon=True
    )

    thread1.start()
    tester_ready.wait()  # Wait until the tester is ready
    thread2.start()
    output_thread.start()

    # Keep the main thread alive
    thread1.join()
    thread2.join()


if __name__ == "__main__":
    main()
