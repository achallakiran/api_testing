import requests
import threading
import time
import json
import csv
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, median
import numpy as np
import matplotlib.pyplot as plt
from jinja2 import Template
import os
import sys

class APILoadTester:
    def __init__(self, input_file, num_parallel_connections=100):
        self.input_file = input_file
        self.num_parallel_connections = num_parallel_connections
        self.results = defaultdict(list)
        self.lock = threading.Lock()
        self.plot_counter = 1

    def load_test(self):
        with open(self.input_file, 'r') as file:
            reader = csv.DictReader(file, delimiter=",",quotechar="'")
            with ThreadPoolExecutor(max_workers=self.num_parallel_connections) as executor:
                for row in reader:
                    api = row['API']
                    method = row['Method']
                    data = json.loads(row.get('Data', '{}'))
                    for _ in range(self.num_parallel_connections):
                        executor.submit(self.send_request, api, method, data)

    def send_request(self, api, method, data):
        start_time = time.time()
        try:
            if method.upper() == 'POST':
                response = requests.post(api, headers={},json=data)
            elif method.upper() == 'GET':
                response = requests.get(api, params=data)
            else:
                raise ValueError("Invalid HTTP method")
            response_time = time.time() - start_time
            with self.lock:
                self.results[api].append(response_time)
        except Exception as e:
            print(f"Error occurred while accessing {api}: {e}")

    def generate_reports(self):
        self.generate_text_report()
        self.generate_html_report()

    def generate_text_report(self):
        with open('text_report.txt', 'w') as file:
            for api, response_times in self.results.items():
                file.write(f"API: {api}\n")
                file.write(f"Average Response Time: {mean(response_times)} seconds\n")
                file.write(f"Minimum Response Time: {min(response_times)} seconds\n")
                file.write(f"Maximum Response Time: {max(response_times)} seconds\n")
                file.write(f"Median Response Time: {median(response_times)} seconds\n")
                file.write(f"95th Percentile Response Time: {np.percentile(response_times, 95)} seconds\n")
                file.write(f"Standard Deviation: {np.std(response_times)} seconds\n\n")

    def generate_html_report(self):
        html_template = """
        <html>
        <head>
            <title>API Load Test Report</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                }
                h1 {
                    color: #333;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                img {
                    display: block;
                    margin: auto;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <h1>API Load Test Report</h1>
            <h2>Response Time Summary</h2>
            <table>
                <tr>
                    <th>API</th>
                    <th>Average Response Time (seconds)</th>
                    <th>Minimum Response Time (seconds)</th>
                    <th>Maximum Response Time (seconds)</th>
                    <th>Median Response Time (seconds)</th>
                    <th>95th Percentile Response Time (seconds)</th>
                    <th>Standard Deviation (seconds)</th>
                </tr>
                {% for api, response_times in results.items() %}
                <tr>
                    <td>{{ api }}</td>
                    <td>{{ average_response_time(response_times) }}</td>
                    <td>{{ min(response_times) }}</td>
                    <td>{{ max(response_times) }}</td>
                    <td>{{ median(response_times) }}</td>
                    <td>{{ percentile_95(response_times) }}</td>
                    <td>{{ std_dev(response_times) }}</td>
                </tr>
                {% endfor %}
            </table>
            <h2>Response Time Graphs</h2>
            {% set plot_counter = 1 %}
            {% for api, response_times in results.items() %}
            <h3>{{ api }}</h3>
            <img src="plots/plot{{ loop.index }}.png" alt="{{ api }} Response Time Graph">
            {% set plot_counter = plot_counter + 1 %}
            {% endfor %}
        </body>
        </html>
        """

        template = Template(html_template)
        with open('html_report.html', 'w') as file:
            file.write(template.render(results=self.results, 
                                       average_response_time=mean, 
                                       min=min, 
                                       max=max, 
                                       median=median, 
                                       percentile_95=lambda x: np.percentile(x, 95),
                                       std_dev=np.std, 
                                       plot_counter=self.plot_counter))

        # Create a directory to save PNG files if it does not exist
        if not os.path.exists('plots'):
            os.makedirs('plots')

        markers = ['o', 's', '^', 'D', 'v']  # Different marker styles for each API
        colors = ['b', 'g', 'r', 'c', 'm']    # Different colors for each API

        for i, (api, response_times) in enumerate(self.results.items()):
            plt.figure()  # Create a new figure for each plot
            plt.plot(response_times, marker=markers[i % len(markers)], linestyle='-', color=colors[i % len(colors)])  # Plot all response times together with markers
            plt.title(f'{api} Response Time')
            plt.xlabel('Request')
            plt.ylabel('Response Time (seconds)')
            plt.savefig(os.path.join('plots', f'plot{self.plot_counter}.png'))  # Save the plot in the 'plots' directory
            plt.close()
            self.plot_counter += 1

if __name__ == "__main__":
    if len(sys.argv) == 2:
        num_connections = int(sys.argv[1])
    else:
        num_connections = 100  # Default number of connections

    tester = APILoadTester("input_file.csv", num_parallel_connections=num_connections)
    tester.load_test()
    tester.generate_reports()
