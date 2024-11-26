# dodns - Small python script for using DigitalOcean as a dynamic DNS service 

This is a small python script that periodically updates existing `A` and `AAAA` records managed through DigitalOcean's nameservers.

This script is tailored to my homeserver setup (using IPv4 and IPv6 and a single domain with multiple subdomains). You are encouraged to modify this script or write your own. DigitalOcean's API is trivially easy to use, especially with their own Python bindings.

The script is configured through environment variables:
- `DODNS_DOMAIN`: the domain you want to manage (e.g. `example.com`)
- `DODNS_RECORDS`: a comma-seperated list of subdomains (e.g. `sub1,sub2,*.sub3` for `sub1.example.com,...`)
- `DIGITALOCEAN_TOKEN`: your DigitalOcean API token, make sure to generate this with the necessary permissions only (list and update domain records)
- `SLEEP_DURATION`: duration this script sleeps for in seconds, default 3600s

The script only updates the existing records if the IP adress of the server has changed. Also note that **the script does not create records**, you will need to create initial A and AAAA records for each subdomain.

If you want to use this in your docker compose deployment:

```yaml
services:
  dodns:
    image: paxplay/dodns # not publically available at the moment, build yourself!
    container_name: digitalocean-dyn-dns
    secrets: ['DODNS_DIGITALOCEAN_TOKEN']

    environment:
      DIGITALOCEAN_TOKEN_FILE: '/run/secrets/DODNS_DIGITALOCEAN_TOKEN'
      DODNS_DOMAIN: 'example.com'
      DODNS_RECORDS: 'sub1,*.sub2,sub3'
      DODNS_SLEEP_DURATION: '3600'
    networks:
      - ip6net

networks:
  ip6net: # needed for ipv6
    enable_ipv6: true
    ipam:
      config:
        - subnet: 2001:db8::/64

secrets:
  DODNS_DIGITALOCEAN_TOKEN:
    file: './secrets/dodns/DIGITALOCEAN_TOKEN'

```
