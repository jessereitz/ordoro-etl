# Ordoro ETL Coding Test
This is the finished product for my solution for Ordoro's ETL coding test. This
simple Python3 program makes a request to a given API for JSON format, cleans it
based on the given parameters, and posts it back to that same API in JSON format
(see below for specifics).

## Installation and Operation

Once downloaded, navigate to the `ordoro-etl` directory. From there run the
`install` script to install all dependencies in a virtual environment. To run,
simply run the `run` script.

Alternatively, the program can be imported as a module and run as such:

```python
from main import main
main()
```

*The automated installation process assumes you are operating on a Unix-like
machine with Python3 and Virtualenv already installed. This has been tested on
Linux (Ubuntu 18.04) and Mac OS (10.14).*

## Libraries Used
* [json](https://docs.python.org/3.6/library/json.html) - Built-in Python library for manipulating JSON data. Used to convert
JSON from API GET request to Python dict and back again before POSTing back to
the API.
* [arrow](https://arrow.readthedocs.io/en/latest/) - Simple datetime utility for
Python. Used to convert the given ISO-8601 timestrings to Python datetime object and for timezone
normalization.
* [requests](http://docs.python-requests.org/en/master/) - Simple HTTP requests
utility for Python. Used to make the GET and POST calls to the API.
* [virtualenv](https://virtualenv.pypa.io/en/stable/) - Virtual environment
utility

## Program Format
The program centers on one main function: clean_data

#### clean_data
This function iterates through each login object obtained from the API and attempts
to place the email in a Python set (sets only allow unique values, so duplicate
emails are thrown out automatically). It then increments the count for logins
associated with a given domain. It then converts and normalizes the
associated timestring to see if the login was in April. If it was, then it
attempts to place the email associated with that login in a separate set (this
is done because we want a list of distinct users who logged in during April,
not the number of distinct logins). It then converts each set to a list and
returns them as part of a single dictionary.

#### Helper Functions
Apart from this there are a few helper functions to maintain modularity and a
main function to actually take care of running everything.


## Time Complexity
Overall, the program iterates over **all** the incoming API data just once, in
clean_data. Here, it is pared down using built-in Python sets
(which are automatically hashed under the hood and are quick with determining/
enforcing uniqueness) and the domain names are counted (using a dictionary to
keep track of the counts). Without taking in to account Python's implementation of
sets and dictionaries, this results in a complexity of about O(n).
