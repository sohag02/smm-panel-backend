import asyncio
import os
import dotenv
from models import Service
from supabase import Client, create_client
from typing import Optional
from models import OrderStatus

dotenv.load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


async def update_order_status(order_id: int, status: str):  # Change type to str
    if status not in [status.value for status in OrderStatus]:  # Validate against OrderStatus
        raise ValueError(f"Invalid status: {status}. Must be one of {[status.value for status in OrderStatus]}.")
    
    res = await (
        supabase.table("orders")
        .update({"status": status})
        .eq("id", order_id)
        .execute()
    )
    return res

def refund_order(order_id: int):
    res = (
        supabase.table("orders")
        .select("*")
        .eq("id", order_id)
        .execute()
    )
    user_id = res.data[0]["user_id"]
    cost = res.data[0]["cost"]
    balance = (
        supabase.table("balances")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    current_balance = balance.data[0]["balance"]
    print(current_balance)
    new_balance = current_balance + cost
    print(new_balance)
    up = (
        supabase.table("balances")
        .update({"balance": new_balance})
        .eq("user_id", user_id)
        .execute()
    )
    return up
    

async def rename_service_in_db(old_name: str, new_name: str):
    res = await (
        supabase.table("services")
        .update({"name": new_name})
        .eq("name", old_name)
        .execute()
    )
    return res

async def add_service(name: str, description:str=None, price: int=None):
    res = await (
        supabase.table("services")
        .insert({
            "name": name,
            "description": description or None,
            "price": price or None
        })
        .execute()
    )
    return res

async def get_services() -> list[Service]:
    res = await (
        supabase.table("services")
        .select("*")
        .execute()
    )
    return res.data
 
async def update_service(id: int, service: Optional[Service]):
    res = await (
        supabase.table("services")
        .update(service)  # Use the service parameter directly
        .eq("id", id)
        .execute()
    )
    return res

if __name__ == "__main__":
    r = refund_order(11)
    print(r)