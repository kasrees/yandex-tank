#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import sys

import aiohttp

from tee import Tee


import time
import datetime

from aiohttp import ClientSession, ClientError

async def get_provider_list(session):
    providers_url = 'http://bepool-qa.travelline.lan/api/rest/inventory/provider/list'
    headers = {
        'X-Inventory-ApiKey': '75010639-0955-4c90-aaaa-4c2b41544edb'
    }
    start_time = time.time()
    async with session.get(providers_url, headers=headers, ssl=False) as response:
        elapsed_time = time.time() - start_time
        try:
            response_data = await response.json()
        except aiohttp.ContentTypeError:
            response_data = None
        return response.status, response_data, elapsed_time


def make_ammo(method, url, headers, case, body):
    """ makes phantom ammo """
    # http request w/o entity body template
    req_template = (
        "%s %s HTTP/1.1\r\n"
        "%s\r\n"
        "\r\n"
    )

    # http request with entity body template
    req_template_w_entity_body = (
        "%s %s HTTP/1.1\n"
        "%s\n"
        "Content-Length: %d\n"
        "\n"
        "%s\n"
    )

    if not body:
        req = req_template % (method, url, headers)
    else:
        req = req_template_w_entity_body % (method, url, headers, len(body), body)

    # phantom ammo template
    ammo_template = (
        "%d %s\n"
        "%s"
    )

    return ammo_template % (len(req), case, req)



async def main():
    client_owner_token = ""
    async with aiohttp.ClientSession() as session:

        provider_status, provider_data, provider_time = await get_provider_list(session)
        if provider_status == 200:
            provider_items = provider_data.get("Items", [])

        providers = provider_items[:3]    

        for provider in providers:
            property_id = str(provider).strip()
            method = "GET".strip()
            url = f"/BookingReport/WebApi/PartnerApi/GetBookings?ProviderId={property_id}&LastModifiedMillisecondsFrom=1230757200000&LastModifiedMillisecondsTo=1262293200000&WithoutDate=True&limit=1001".strip()
            case = "".strip()
            body = None
            headers = "Host: bookingreport-qa.travelline.lan:443\r\n" + \
                      "User-Agent: tank\r\n" + \
                      "Accept: */*\r\n" + \
                      "Content-Type: application/json\r\n" + \
                      "Connection: close\r\n"

            sys.stdout.write(make_ammo(method, url, headers, case, body))

if __name__ == "__main__":
    with open('../loadtest/ammo.txt', 'w') as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)
        try:
            asyncio.run(main())
        finally:
            sys.stdout = original_stdout


