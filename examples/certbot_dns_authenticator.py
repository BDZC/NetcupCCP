#!/usr/bin/env python3
# coding: utf8

# Copyright (C) 2018 MrKrabat
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import time

import netcup

'''
Certbot command:
certbot certonly --manual --preferred-challenges=dns --manual-auth-hook authenticator.py --manual-cleanup-hook cleanup.py -d *.domain.tld -d domain.tld
'''

def getNetcupDomain(fqdn):
    """
    Returns domainname for netcup ccp
    """
    for key, value in DOMAIN_LIST.items():
        if value == fqdn or "*." + value == fqdn:
            return "_acme-challenge"
        elif value in fqdn:
            return "_acme-challenge." + fqdn[:-(len(value)+1)]


def getDomainID(fqdn):
    """
    Returns domain id
    """
    for key, value in DOMAIN_LIST.items():
        if value in fqdn:
            return key


# connect to cpp
ccp = netcup.CCPConnection(cachepath="mysession")
ccp.start(username = "<CCP LOGIN>",
          password = "<CCP PASSWORD>")

# get data
DOMAIN_LIST        = {"000001": "domain1.tld", "000002": "domain2.tld"} # list of all netcup domains + keys
DOMAIN_ID          = getDomainID(os.environ["CERTBOT_DOMAIN"])
CERTBOT_DOMAIN     = getNetcupDomain(os.environ["CERTBOT_DOMAIN"])
CERTBOT_VALIDATION = os.environ["CERTBOT_VALIDATION"]

# get domain infos
mydomain = ccp.getDomain(DOMAIN_ID)

# add acme challenge
mydomain.addRecord(rr_host        = CERTBOT_DOMAIN,
                   rr_type        = "TXT",
                   rr_destination = CERTBOT_VALIDATION)

# save changes
ccp.saveDomain(mydomain)

# wait for changes to take effect
timer = time.time() + 15*60
while True:
    time.sleep(60)
    # check if settings are live or timeout reached
    if ccp.isRecordLive(DOMAIN_ID) or time.time() > timer:
        break

# cleanup
ccp.close()
