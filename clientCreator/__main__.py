import aiohttp
import asyncio
import time
import datetime
import sys
import jwt
from aiohttp import ClientSession, ClientError

class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

async def get_jwt_token(session):
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

def decode_token_expiry(token):
    payload = jwt.decode(token, options={"verify_signature": False})
    return payload.get('exp', 0)

async def get_valid_token(session):
    global token, token_expiry
    current_time = time.time()
    if current_time > token_expiry - 300:
        print("Token is expired or about to expire, refreshing token...")
        token = await get_jwt_token(session)
        token_expiry = decode_token_expiry(token)
    return token

async def get_all_partners(session):
    token = await get_valid_token(session)
    partners_url = 'https://partneraccessmanagement.travelline.lan/PartnerAccessManagement/Api/api/partners'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    async with session.get(partners_url, headers=headers, ssl=False) as response:
        response.raise_for_status()
        partners = await response.json()
        return partners

async def delete_partner(session, partner_id):
    token = await get_valid_token(session)
    delete_url = f'https://partneraccessmanagement.travelline.lan/PartnerAccessManagement/Api/api/partners?partnerId={partner_id}'
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {token}'
    }
    start_time = time.time()
    async with session.delete(delete_url, headers=headers, ssl=False) as response:
        elapsed_time = time.time() - start_time
        response.raise_for_status()
        return response.status, None, elapsed_time

async def make_api_request(session, partner_id):
    token = await get_valid_token(session)
    api_url = 'https://partneraccessmanagement.travelline.lan/PartnerAccessManagement/Api/api/partners'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        "partnerId": partner_id
    }
    start_time = time.time()
    async with session.post(api_url, headers=headers, json=data, ssl=False) as response:
        elapsed_time = time.time() - start_time
        try:
            response_data = await response.json()
        except aiohttp.ContentTypeError:
            response_data = None
        return response.status, response_data, elapsed_time

async def enable_partner(session, partner_id):
    token = await get_valid_token(session)
    enable_url = f'https://partneraccessmanagement.travelline.lan/PartnerAccessManagement/Api/api/partners/{partner_id}/enable'
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {token}'
    }
    start_time = time.time()
    async with session.post(enable_url, headers=headers, ssl=False) as response:
        elapsed_time = time.time() - start_time
        try:
            response_data = await response.json()
        except aiohttp.ContentTypeError:
            response_data = None
        return response.status, response_data, elapsed_time

async def assign_service_account_roles(session, partner_id):
    token = await get_valid_token(session)
    roles_url = f'https://partneraccessmanagement.travelline.lan/PartnerAccessManagement/Api/api/partners/{partner_id}/service-accounts-roles'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "roleType": "api_access_catalog",
        "role": "reservation_api"
    }
    start_time = time.time()
    async with session.post(roles_url, headers=headers, json=data, ssl=False) as response:
        elapsed_time = time.time() - start_time
        try:
            response_data = await response.json()
        except aiohttp.ContentTypeError:
            response_data = None
        return response.status, response_data, elapsed_time

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

async def add_resource_to_partner(session, partner_id, resource_id):
    token = await get_valid_token(session)
    resource_url = f'https://partneraccessmanagement.travelline.lan/PartnerAccessManagement/Api/api/accesses/partners/{partner_id}/resources'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "resourceId": str(resource_id),
        "resourceType": "property"
    }
    start_time = time.time()
    async with session.post(resource_url, headers=headers, json=data, ssl=False) as response:
        elapsed_time = time.time() - start_time
        try:
            response_data = await response.json()
        except aiohttp.ContentTypeError:
            response_data = None
        return response.status, response_data, elapsed_time

def get_partners_list(count):
    return [f"load_test_partner_{i+1}" for i in range(count)]

async def handle_partner_operation(session, partner_id, operation_func, operation_desc, semaphore, *args, retries=3):
    async with semaphore:
        for attempt in range(retries):
            try:
                status, data, elapsed_time = await operation_func(session, partner_id, *args)
                print(f"Partner {partner_id} {operation_desc} took {elapsed_time:.2f} seconds")
                if status == 200:
                    return True, data
                else:
                    print(f"Failed to {operation_desc} partner {partner_id}: {data}")
                    return False, data
            except ClientError as e:
                print(f"Partner {partner_id} generated an exception during {operation_desc}: {e}")
                if attempt == retries - 1:
                    return False, str(e)
                await asyncio.sleep(2 ** attempt)  # экспоненциальная задержка перед повторной попыткой
            except Exception as e:
                print(f"Partner {partner_id} generated an unexpected exception during {operation_desc}: {e}")
                return False, str(e)

async def main():
    print(f"Start time: {datetime.datetime.now()}")
    global token, token_expiry
    partners = get_partners_list(100)
    max_concurrent_requests = 2  # Максимальное количество одновременных запросов
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        token = await get_jwt_token(session)
        token_expiry = decode_token_expiry(token)

        # print(f"Start delete time: {datetime.datetime.now()}")
        # # Удаляем старые данные
        # all_partners = await get_all_partners(session)
        # while len(all_partners) != 0:
        #     delete_tasks = [
        #         handle_partner_operation(session, partner['partnerId'], delete_partner, "deletion", semaphore)
        #         for partner in all_partners
        #     ]
        #     await asyncio.gather(*delete_tasks)
        #     all_partners = await get_all_partners(session)

        print(f"Start create time: {datetime.datetime.now()}")
        # Создаем новых партнеров
        create_tasks = [handle_partner_operation(session, partner, make_api_request, "creation", semaphore) for partner in partners]
        create_results = await asyncio.gather(*create_tasks)

        print(f"Start enable time: {datetime.datetime.now()}")
        enable_tasks = []
        for partner in partners:
            # if success:
            enable_task = handle_partner_operation(session, partner, enable_partner, "enabling", semaphore)
            enable_tasks.append(enable_task)

        enable_results = await asyncio.gather(*enable_tasks)

        print(f"Start assign role time: {datetime.datetime.now()}")
        assign_roles_tasks = []
        for partner, (success, data) in zip(partners, enable_results):
            # if success:
            assign_roles_task = handle_partner_operation(session, partner, assign_service_account_roles, "assigning service account roles", semaphore)
            assign_roles_tasks.append(assign_roles_task)

        await asyncio.gather(*assign_roles_tasks)

        print(f"Start get provider list time: {datetime.datetime.now()}")
        # Get provider list
        provider_status, provider_data, provider_time = await get_provider_list(session)
        print(f"Getting provider list took {provider_time:.2f} seconds")
        if provider_status == 200:
            provider_items = provider_data.get("Items", [])
            print("Provider list count:", len(provider_items))
        else:
            print("Failed to get provider list:", provider_data)
            return

        print(f"Start add resource time: {datetime.datetime.now()}")
        # Assign a provider to each partner
        resource_tasks = []
        for partner, resource_id in zip(partners, provider_items):
            resource_task = handle_partner_operation(session, partner, add_resource_to_partner, "adding resource", semaphore, resource_id)
            resource_tasks.append(resource_task)

        await asyncio.gather(*resource_tasks)

        print(f"End time: {datetime.datetime.now()}")

if __name__ == "__main__":
    with open('output.txt', 'w') as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)
        try:
            asyncio.run(main())
        finally:
            sys.stdout = original_stdout
