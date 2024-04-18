import os
import coverage

class CoAPCoverageMiddleware:
  
    def __init__(self):
        self.cov = coverage.Coverage()

    def start_coverage(self):
        self.cov.start()

    def stop_coverage(self):
        self.cov.stop()
        self.cov.save()
        self.cov.report()

    def get_coverage_data(self):
        cov_data = self.cov.get_data()
        covered_lines_per_file = {}
        for filename in cov_data.measured_files():
            basename = os.path.basename(filename)
            covered_lines_per_file[basename] = [lineno for lineno in cov_data.lines(filename) if lineno != 0]
        return covered_lines_per_file

    def analyze_coverage(self):
        coverage_count_dict = {}
        covered_lines_per_file = self.get_coverage_data()
        for filename, line_numbers in covered_lines_per_file.items():
            line_count = {}
            for line_number in line_numbers:
                line_count[line_number] = line_count.get(line_number, 0) + 1
            coverage_count_dict[filename] = line_count
        return coverage_count_dict

# Example usage:
# if __name__ == "__main__":
#     analyzer = CoverageAnalyzer()
#     analyzer.start_coverage()
#     # Perform actions that you want to measure coverage for
#     # For example, execute your CoAP functionality
#     # Then stop and analyze coverage
#     analyzer.stop_coverage()
#     coverage_data = analyzer.analyze_coverage()
#     print(coverage_data)
