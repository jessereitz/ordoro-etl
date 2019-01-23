import json
import arrow
import requests

API_URL = 'https://us-central1-marcy-playground.cloudfunctions.net/ordoroCodingTest'
MY_EMAIL = 'jessereitz1@gmail.com'

def get_data():
    raw_data = requests.get(API_URL)
    return raw_data.json()['data']

def post_data(raw_dict):
    json_dump = json.dumps(raw_dict)
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(API_URL, headers=headers, data=json_dump)
    return r

def distinct_emails(raw_data):
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

        Return Format:
            {'email@email.com', 'email2@email2.com'}
    """
    distinct_emails = set()
    for dict in raw_data:
        if dict.get('email') and '@' and '.' in dict.get('email'):
            distinct_emails.add(dict['email'])
    return list(distinct_emails)

def domain_counts(distinct_emails):
    """
        Determines the number of users from domains which have more than one
        user logging in.

        Iterates over each email address and determines the number of times each
        unique domain appears in the iterable. If this amount is greater than one,
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

def april_logins(raw_data):
    """
        Iterates over given list of dicts, converts and normalizes dates to UTC,
        returns all login dates in April.
    """
    datestr = '%Y-%m-%dT%H:%M:%S%z'
    apr_login = []
    for login in raw_data:
        try:
            dt = arrow.get(login.get('login_date'))
            if dt.month == 4:
                apr_login.append(login)
        except:
            print('uh oh')
    return distinct_emails(apr_login)

def main():
    data = get_data()
    unique_emails = distinct_emails(data)
    cleaned_data = {
        "your_email_address": "jessereitz1@gmail.com",
        "unique_emails": unique_emails,
        "user_domain_counts": domain_counts(unique_emails),
        "april_emails": april_logins(data)
    }
    r = post_data(cleaned_data)
    return r
