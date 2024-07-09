#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import sys

import aiohttp

from tee import Tee


async def get_client_owner_jwt_token(session):
    token_url = 'https://keycloak.travelline.lan/realms/PartnerApi/protocol/openid-connect/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': 'load_test_client_owner',
        'client_secret': 'cFy2DjpNs41jRQhKfEAp8PvAACWhJHFm'
    }
    async with session.post(token_url, data=token_data, ssl=False) as response:
        response.raise_for_status()
        result = await response.json()
        return result.get('access_token')

async def get_client_jwt_token(session, client_id, client_secret):
    token_url = 'https://keycloak.travelline.lan/realms/PartnerApi/protocol/openid-connect/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': f'{client_id}',
        'client_secret': f'{client_secret}'
    }
    async with session.post(token_url, data=token_data, ssl=False) as response:
        response.raise_for_status()
        result = await response.json()
        return result.get('access_token')


async def get_client_secrets(session, client_owner_token, client_id):
    url = f'https://partneraccessmanagement.travelline.lan/PartnerAccessManagement/Api/api/partners/{client_id}/client-secrets'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {client_owner_token}'
    }

    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        result = await response.json()
        return result.get('secret')


async def fetch_resources(session, client_owner_token, client_id):
    url = f'https://partneraccessmanagement.travelline.lan/PartnerAccessManagement/Api/api/accesses/partners/{client_id}/resources'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {client_owner_token}'
    }

    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        result = await response.json()
        return result.get('resources')[0].get('resourceId')


def make_ammo(method, url, headers, case, body):
    """ makes phantom ammo """
    # http request w/o entity body template
    req_template = (
        "%s %s HTTP/1.1\n"
        "%s\n"
        "\n"
    )

    # http request with entity body template
    req_template_w_entity_body = (
        "%s %s HTTP/1.1\r\n"
        "%s\r\n"
        "Content-Length: %d\r\n"
        "\r\n"
        "%s\r\n"
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

    return ammo_template % (len(req) + 8, case, req)


def get_partners_list(count):
    return [f"load_test_partner_{i+1}" for i in range(count)]


async def main():
    client_owner_token = ""
    async with aiohttp.ClientSession() as session:
        client_owner_token = await get_client_owner_jwt_token(session)

        partners = get_partners_list(100)

        for partner in partners:
            partner_secret = await get_client_secrets(session, client_owner_token, partner)
            partner_token = await get_client_jwt_token(session, partner, partner_secret)
            # property_id = await fetch_resources(session, client_owner_token, partner)

            method = "GET".strip()
            url = f"/resources/available-properties".strip()
            case = "".strip()
            body = None
            headers = "Host: localhost:5000\n" + \
                      "User-Agent: tank\n" + \
                      "Accept: */*\n" + \
                      "Content-Type: application/json\n" + \
                      "Connection: keep-alive\n" + \
                      f"Authorization: Bearer {partner_token.strip()}"

            sys.stdout.write(make_ammo(method, url, headers, case, body))

if __name__ == "__main__":
    with open('../loadtest/ammo.txt', 'w') as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)
        try:
            asyncio.run(main())
        finally:
            sys.stdout = original_stdout


