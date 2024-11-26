import os
import sys
import pydo
import requests
import time

RECORDS = os.environ.get('DODNS_RECORDS', default='').split(',')
DOMAIN = os.environ.get('DODNS_DOMAIN')
SLEEP_DURATION = int(os.environ.get('DODNS_SLEEP_DURATION', default='3600'))
DIGITALOCEAN_TOKEN=os.environ.get('DIGITALOCEAN_TOKEN', default=None)
if DIGITALOCEAN_TOKEN == None and 'DIGITALOCEAN_TOKEN_FILE' in os.environ:
    with open(os.environ.get('DIGITALOCEAN_TOKEN_FILE')) as f:
        DIGITALOCEAN_TOKEN = f.read().strip()

if DOMAIN is None:
    print('No Domain specified')
    exit(1)

client = pydo.Client(token=DIGITALOCEAN_TOKEN)

def get_ip():
    ipv4, ipv6 = None, None

    try:
        ipv4 = requests.get('https://myipv4.p1.opendns.com/get_my_ip').json()['ip']
    except:
        print(f'Failed to retrieve ipv4 adress')

    try:
        ipv6 = requests.get('https://myipv6.p1.opendns.com/get_my_ip').json()['ip']
    except:
        print(f'Failed to retrieve ipv6 adress')

    return ipv4, ipv6

def get_record(name, record_type, records):
    candidates = list(filter(lambda r: r['name'] == name and r['type'] == record_type, records))
    if len(candidates) == 0:
        print(f'No candidates matching [{record_type}] {name}')
    elif len(candidates) > 1:
        print(f'Found multiple candidates matching [{record_type}] {name}')
    else:
        return candidates[0]

    return None

def update_records(domain_name, record_list, existing_records, ipv4, ipv6=None):
    for record in record_list:
        a_record = get_record(record, 'A', existing_records)
        aaaa_record = get_record(record, 'AAAA', existing_records)
        print(f'updating records for {record}.{domain_name}:', end='')
        
        if a_record and ipv4 != None:
            update_record(domain_name, a_record, ipv4)
        if aaaa_record and ipv6 != None:
            update_record(domain_name, aaaa_record, ipv6)

        print('')

def update_record(domain_name, record, ip):
    print(f' [{record["type"]}] ', end='')
    if record['data'] == ip:
        print(f'already correct', end='')
    else:
        client.domains.update_record(domain_name=domain_name, domain_record_id=record['id'], body={'data': ip})
        print(f'updated', end='')

if __name__ == '__main__':
    print(f'DigitalOcean DNS Update Script --- Domain: {DOMAIN}; Records: {RECORDS}')
    sys.stdout.flush() # python docker container doesn't automatically flush?!

    old_ipv4, old_ipv6 = None, None

    while True:
        print(f'-------- UPDATE RECORD ATTEMPT {time.asctime()} --------')
        ipv4, ipv6 = get_ip()
        if ipv4 == old_ipv4 and ipv6 == old_ipv6:
            print(f'IP adresses haven\'t changed since last attempt')
        else:
            print(f'Retrieved IP adresses --- v4: {ipv4}, v6: {ipv6}')
            existing_records = client.domains.list_records(domain_name=DOMAIN)
            update_records(DOMAIN, RECORDS, existing_records['domain_records'], ipv4, ipv6)

        old_ipv4, old_ipv6 = ipv4, ipv6
        print(f'Sleeping for {SLEEP_DURATION}s')
        sys.stdout.flush() # python docker container doesn't automatically flush?!
        time.sleep(SLEEP_DURATION)

