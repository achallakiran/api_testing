# api_testing
My repository to hold all codes related to api testing e.g load testing scripts, karate scripts etc

api_load_test.py is a simple utility that provides time series response time graph for GET and POST APIs
and common metrics used for load testing like average response time, least response time, max response time, 
median response time, 95 percentile response time. The scripts expects a file containing the list og GET or 
POST APIs in an input file.


Input File: input_file.csv contains information about the apis to be called
call the script using: python3 api_load_test.py 
Default number of parallel connections: 100. Can be passed from the command line also as the first argument.
