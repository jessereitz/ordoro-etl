"""
    Ordoro ETL

    Goal - GET data from given API then POST it back in specified form.
        1. List of distinct email addresses
        2. # of users per domain if domain has more than 1 user
        3. Email of users who signed in during April

    Given:
    {
        "data": [
            {"email": "email@email.com", "login_date": "2014-04-10T11:22:33+00:00"},
        ]
    }

    Expected:
    {
        "your_email_address": "jessereitz1@gmail.com",
        "unique_emails": ["email1@test.com", "email2@test.com"],
      "user_domain_counts": {
          "bing.com": 2,
          "sling.com": 3
      },
      "april_emails": ["email1@test.com", "email2@test.com"]
  }
"""

import requests

def get_cleaned_data():
    raw_data = requests.get('https://us-central1-marcy-playground.cloudfunctions.net/ordoroCodingTest')
    data = raw_data.json()['data']
    return data

def distinct(raw_data):
    """
        Returns a set of emails found in the given raw data.

        Iterates over given raw_data of format {'email': 'email@email.com',
        'login_date': 'login date'} and places them in a set. If any given dict does not contain a field 'email' with a
        reasonably valid email address, it is discarded.

        Assumptions:
            raw_data is list of dictionaries of format:
                {
                    'login_date': 'datetime_string',
                    'email': 'email@domain.com'
                }
            If email does not contain '@' or at least one '.', dict is discarded
    """
    distinct_emails = set()
    for dict in raw_data:
        if dict.get('email') and '@' and '.' in dict.get('email'):
            distinct_emails.add(dict['email'])
    return distinct_emails

def domain_counts(distinct_emails):
    """
        Determines the number of users from domains which have more than one
        user logging in.

        Iterates over each email address and determines the number of times each
        unique domain appears in the list. If this amount is greater than one,
        it is added to a final_counts dictionary and returned.

        Assumptions:
            Given list or set contains only unique emails.
            Emails in given list are in the standard email address format
                (username@domain.com, user.name@subdomain.domain.com)

        Return Format:
            {
                'domain.com': int,
                'gmail.com': 17
            }
    """
    # runtime of O(n)
    domain_counts = {}
    final_count = {}
    for email in distinct_emails:
        domain = email.split('@')[-1]
        if final_count.get(domain):
            # if domain is already in the final, increment it
            final_count[domain] += 1
        elif domain_counts.get(domain):
            # if this is the second time seeing the domain, put it in final_count
            final_count[domain] = domain_counts[domain]
        else:
            # otherwise put it in the initial count
            domain_counts[domain] = 1

    return final_count


def main():
    raw_data = requests.get('https://us-central1-marcy-playground.cloudfunctions.net/ordoroCodingTest')
    data = raw_data.json()['data']
