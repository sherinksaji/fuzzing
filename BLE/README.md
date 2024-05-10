# BLE Fuzzer

Our group project focuses on developing a general automated fuzzing framework that fuzzes 3 targets - a Django Web Application, CoAP, Bluetooth Low Energy (BLE) Zephyr stack. The following are the key components of the project.

## AFL_Fuzzer Class in AFL_base.py

The foundation of our framework, providing AFL methods like ChooseNext, AssignEnergy, and IsInteresting for seed selection and mutation. This is kept general and to be used to fuzz all 3 targets.

## Mutator in mutator.py

A modular Mutator class designed to mutate test inputs, t, intelligently, accommodating various data types such as strings, integers, and arrays.

## BLE_Fuzzer Class

An extension of the AFL_base class, tailored specifically for BLE fuzzing. It incorporates abstract methods like mutate_t and runTestRevealsBug for BLE-specific operations.This part of the repo focuses on fuzzing BLE Zephyr stack.

## run_ble_original.py

A subprocess script responsible for coordinating fuzzing activities, interacting with Zephyr.exe, and detecting bugs or crashes in the BLE implementation.

## Fuzzing Workflow:

### Seed Selection

Inputs are selected based on their potential to explore new paths, utilizing coverage data and frequency-based energy assignment to prioritize exploration.

### Mutation

Selected inputs undergo mutation using the Mutator class, generating a diverse set of test cases for fuzzing.

### Test Execution

Fuzzed inputs are executed against the BLE implementation, with run_ble_original.py orchestrating the testing process and detecting anomalies.

### Coverage Analysis

Coverage information is collected to assess the effectiveness of test cases in exploring different execution paths.

### Bug Detection

Bugs or crashes detected during testing are reported and analyzed, aiding in the identification and resolution of vulnerabilities.

## Outcome:

The framework generates comprehensive reports detailing test outcomes, coverage metrics, and detected bugs, empowering developers to enhance the reliability and security of their BLE implementations.

By providing a systematic and automated approach to fuzzing, our framework enables efficient testing and validation of BLE-enabled devices and applications, ensuring robustness and resilience against potential security threats.

**Set up to run:**

```bash
git clone https://github.com/sherinksaji/fuzzing.git
```

Look at generated bugAndCrashReport.txt to see bugs generated.

See ble_fuzzer.py mutate_t function comments to see how can you can uncomment code to reproduce bugs easily.
