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

def get_domain(email):
    """
        Returns the domain from a given email address.
    """
    return email.split('@')[-1]

def count_domain(email, domains_dict):
    """
        Count the number of times we've seen an email domain using the given
        domains_dict. domains_dict must be a dictionary in the format:

            {
                "all": set(),
                "final_count": {}
            }

        where "all" is a set of all the domains we have seen and "final_count"
        is a dictionary containing domains we have seen more than once, along
        with the number of times we have seen it. A set is used for "all"
        because it is faster at determining membership than a list or dict.

        Return Format:
            dictionary: Returns the given domains_dict with updated domain
                counts.
    """
    domain = get_domain(email)
    if domains_dict["final_count"].get(domain):
        # if domain is already in the final, increment it
        domains_dict["final_count"][domain] += 1
    elif domain in domains_dict["all"]:
        # if second time seeing the domain, record it as such in final_count
        domains_dict["final_count"][domain] = 2
    else:
        # otherwise put it in the initial count
        domains_dict["all"].add(domain)
    return domains_dict

def clean_data(raw_data):
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
    domains = {
        "all": set(),
        "final_count": {}
    }
    for login in raw_data:
        # Check that email exists, that it's formatted
        if login.get('email') and '@' and '.' in login.get('email'):
            # Remove trailing/leading whitespace from email
            email = login['email'].strip()

            distinct_emails.add(email)

            domains = count_domain(email, domains)

            if in_april(login):
                april_logins.add(email)

    return {
        "distinct_emails": list(distinct_emails),
        "user_domain_counts": domains["final_count"],
        "april_logins": list(april_logins)
        }

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

    cleaned_data = clean_data(data)
    cleaned_data["your_email_address"] = "jessereitz1@gmail.com"

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
