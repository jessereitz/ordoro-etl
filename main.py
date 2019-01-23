import json
import arrow
import requests

API_URL = 'https://us-central1-marcy-playground.cloudfunctions.net/ordoroCodingTest'
MY_EMAIL = 'jessereitz1@gmail.com'

def get_data():
    """
        Get the JSON data from the designated API endpoint.

        Return Format:
            [Login]: returns a list of logins converted to Python dicts from the
                API.
    """
    raw_data = requests.get(API_URL)
    return raw_data.json()['data']

def post_data(cleaned_dict):
    """
        Post the cleaned data to the designated endpoint.

        Return Format:
            None | Excaption : Returns None if successful. Else raises an
                Exception.
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

def in_april(login):
    """
        Checks if given login is in April. Uses the arrow library to convert the
        given ISO-8601 time string to a Python datetime object, then normalize
        it to UTC.

        Return Format:
            boolean: True if in April. Else False.
    """
    try:
        dt = arrow.get(login.get('login_date')).to('utc')
    except Exception as e:
        return False
    return dt.month == 4


def dist_emails_apr_logins(raw_data):
    """
        Returns a set of emails found in the given raw data.

        Iterates over given raw_data of format {'email': 'email@email.com',
        'login_date': 'login date'} and each in a distinct_emails set. Because
        sets allow only unique objects, duplicate emails are sorted out
        automatically. If any given dict does not contain a field
        'email' with a reasonably valid email address, it is discarded.

        Each login is then checked to see if it was in April. If
        it was, then that login's user's email address is added to the
        april_logins set. Again, a set is used to avoid showing the same user
        twice (we just want to know if they logged in during April, not how many
        times they did so, else we could just use a list).

        Assumptions:
            raw_data is list of dictionaries of format:
                {
                    'login_date': 'datetime_string',
                    'email': 'email@domain.com'
                }
            If email does not contain '@' or at least one '.', dict is discarded

        Return Format:
            Distinct emails and April logins are returned as lists inside a dict.
            {
                'distinct_emails': ['email@email.com', 'email2@email2.com']
                'apil_logins': ['email@email.com', 'email2@email2.com']
            }
    """
    distinct_emails = set()
    april_logins = set()
    for login in raw_data:
        # Check that email exists, that it's formatted
        if login.get('email') and '@' and '.' in login.get('email'):
            email = login['email']

            distinct_emails.add(email)

            if in_april(login):
                april_logins.add(email)
    # Returned as a list for easier manipulation elsewhere
    return {
        "distinct_emails": list(distinct_emails),
        "april_logins": list(april_logins)
        }

def domain_counts(distinct_emails):
    """
        Determines the number of users from domains which have more than one
        user logging in.

        Iterates over each email address and determines the number of times each
        unique domain appears in the iterable. If this amount is greater than one,
        it is added to a final_counts dictionary and returned.

        This is done separately from/after the above function because it is a
        bit more efficient to wait until all unique users are pulled out of the
        larger set of data. Since we want to see the number of users associated
        with a given domain, not the number of logins, we would have to check
        to see if the user had already been put into the set in
        dist_emails_apr_logins for each login which would mean traversing the
        distinct_emails set for every login checked. This way, we just have to
        iterate through the pared-down data one time. If, however, we wanted to
        see how many total logins are associated with a given domain, it would
        be very easy to implement the same method in the dist_emails_apr_logins
        function as is implemented here.

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

        Return Format:
            0 | 1: If successful, exits with 0. Otherwise exits with 1.
    """
    print('Requesting JSON data...')

    data = get_data()

    print('Data received. Cleaning emails, counting domains, and checking who logged in in April...')

    emails_and_logins = dist_emails_apr_logins(data)
    cleaned_data = {
        "your_email_address": "jessereitz1@gmail.com",
        "unique_emails": emails_and_logins['distinct_emails'],
        "user_domain_counts": domain_counts(emails_and_logins['distinct_emails']),
        "april_emails": emails_and_logins['april_logins']
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
    # If called directly, run main.
    main()
