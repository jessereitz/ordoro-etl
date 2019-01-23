import json
import arrow
import requests

API_URL = 'https://us-central1-marcy-playground.cloudfunctions.net/ordoroCodingTest'
MY_EMAIL = 'jessereitz1@gmail.com'

def get_data():
    """
        Get the JSON data from the designated API endpoint.
    """
    raw_data = requests.get(API_URL)
    return raw_data.json()['data']

def post_data(cleaned_dict):
    """
        Post the cleaned data to the designated endpoint.

        If successful, returns None. If not, an exception is raised.
    """
    final_json = json.dumps(cleaned_dict)
    headers = { 'Content-Type': 'application/json' }

    try:
        r = requests.post(API_URL, headers=headers, data=final_json)
    except Exception as e:
        raise e

    if r.status_code != 200 or not r.json():
        # check for complete fail or lack of JSON response
        raise Exception('Post to API failed. JSON response is printed below: \n' + str(r.json()))
    return r
    return None

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
            # try to get the date, see if it's in April, and save it
            dt = arrow.get(login.get('login_date'))
            if dt.month == 4:
                apr_login.append(login)
        except:
            # if there is no associated date, pass over the login
            pass
    return distinct_emails(apr_login)

def main():
    """
        Gets data, cleans it, and returns it to the API in the format:
            {
                "your_email_address": "email@email.com",
                "unique_emails": ["email1@email.com, email2@email.com"],
                "user_domain_counts": {
                    "gmail.com": 2,
                    "hotmail.com": 15
                },
                "april_emails": ["email1@email.com", "email2@email.com"]
            }

        If successful, exits with 0. Otherwise exits with 1.
    """
    print('Requesting JSON data...')

    data = get_data()

    print('Data received. Cleaning emails, counting domains, and checking who logged in in April...')

    unique_emails = distinct_emails(data)
    cleaned_data = {
        "your_email_address": "jessereitz1@gmail.com",
        "unique_emails": unique_emails,
        "user_domain_counts": domain_counts(unique_emails),
        "april_emails": april_logins(data)
    }

    print('Done.')
    print('Posting data to API...')

    try:
        r = post_data(cleaned_data)
        print('Data has been successfully cleaned and resubmitted to API.')
        return r
    except Exception as e:
        print('Something went wrong. See below for more info:')
        print(e)
        return 1
    return 0


if __name__ == '__main__':
    main()
