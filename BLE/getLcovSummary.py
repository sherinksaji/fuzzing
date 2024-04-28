import subprocess
import os

fileName = "lcov_1713322466802813593.info"
fullDir = os.path.join("lcov_coverage", fileName)
lcov_summary_command = f"lcov --rc lcov_branch_coverage=1 --summary {fullDir}"
result = subprocess.run(
    lcov_summary_command, shell=True, text=True, capture_output=True
)

lines_coverage = next(
    (line for line in result.stdout.splitlines() if "lines......:" in line), None
)
if lines_coverage:

    coverage_percentage_with_bracket = lines_coverage.split(":")[1]
    coverage_percentage_str = coverage_percentage_with_bracket.split("%")[0]
    coverage_percentage = float(coverage_percentage_str)

    print(coverage_percentage)
else:
    print(None)
