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
machine with Python3 and Virtualenv already installed.*

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
The program centers on two main functions: dist_emails_apr_logins and domain_counts.

#### dist_emails_apr_logins
The former iterates through each login object obtained from the API and attempts
to place the email in a Python set (sets only allow unique values, so duplicate
emails are thrown out automatically). It then converts and normalizes the
associated timestring to see if the login was in April. If it was, then it
attempts to place the email associated with that login in a separate set (this
is done because we want a list of distinct users who logged in during April,
not the number of distinct logins). It then converts each set to a list and
returns them as part of a single dictionary.

#### domain_counts
This function takes the resulting distinct email list from
dist_emails_apr_logins, iterates over it over it and counts the number of users
associated with each domain. If we were to, instead, want the total number of
logins associated with a given domain, we could implement a similar method in
dist_emails_apr_logins. The method employed is to use two dictionaries: one to keep
track of the first time we see a domain and another to keep track of subsequent
numbers of associated users. Essentially, if a given domain name is already in
initial dictionary, we know there is more than 1 user associated with it and thus
should be returned. By storing these in a separate dictionary, we can easily
return only those domains associated with more than 1 user, along with their
associated user count.

#### Helper Functions
Apart from this there are a few helper functions to maintain modularity and a
main function to actually take care of running everything.


## Time Complexity
Overall, the program iterates over **all** the incoming API data just once, in
dist_emails_apr_logins. Here it, it is pared down using built-in Python sets
(which are automatically hashed under the hood and are quick with determining/
enforcing uniqueness). Without taking in to account Python's implementation of
determining uniqueness in sets, this results in a complexity of about O(n). One
of these sets is then converted to a list and is then iterated over again in the
domain_counts function, again about O(n).

This second iteration is over the list of unique emails produced by dist_emails_apr_logins
and is based on the
assumption we value the number of unique users associated with a domain over the
number of unique logins. If we were to flip it around and look at just the total
number of logins associated with a domain, we would be able to keep that count
as we iterate over the logins the first time. However, as it stands, we would
need to traverse the set in dist_emails_apr_logins for *every* login just to
check if they that person has already been accounted for. This is fine if that
person has only logged in a few times but performance can quickly degrade if
many users log in many, many times. As such, it is better to pare down the
number of logins to just those we value and iterate over them separately.
