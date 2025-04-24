# resolvers.py
from ariadne import QueryType,MutationType,SubscriptionType
from elasticsearch import Elasticsearch
# from elasticsearch import NodeConfig
from queries import get_orders_by_customer, get_customerstats_BasedOnCategory
import asyncio
from datetime import datetime,timedelta
from elasticsearch.helpers import scan
from broadcaster import Broadcast
import json


# Initialize Elasticsearch client
es = Elasticsearch(['http://localhost:9200'])
broadcast = Broadcast("redis://localhost:6379")

async def initialize_broadcast():
    if not hasattr(broadcast, "_pub_conn") or broadcast._pub_conn is None:
        await broadcast.connect()

query = QueryType()
mutation=MutationType()
subscription=SubscriptionType()

#Query resolver to get the orders of the customer
@query.field("ordersByCustomer")
def resolve_orders_by_customer(_, info, customerId):
   
    
    try:
        
        results = es.search(
            index="kibana_sample_data_ecommerce",
            body=get_orders_by_customer(customerId)
        )

        if not results:
            return []

        orders = [
            {
                "order_id": hit["_source"]["order_id"],
                "customer_id": hit["_source"]["customer_id"],
                "customer_full_name": hit["_source"]["customer_full_name"],
                "taxful_total_price": hit["_source"]["taxful_total_price"],
                "order_date": hit["_source"]["order_date"]
            }
            for hit in results["hits"]["hits"]
        ]
        return orders

    except Exception as error:
        print(f"Elasticsearch query error: {error}")
        raise error

#query resolver which gives the customer statisticd based on the particular category   
@query.field("customerstats_BasedOnCategory")
def resolve_customerstats_BasedOnCategory(_,info,category):
    try:
        results=es.search(index="kibana_sample_data_ecommerce",
                          body=get_customerstats_BasedOnCategory(category))
        
        if not results:
            return []
        
        customer_stats=[
            {
                "customerId":int(agg["key"]),
                "avgOrderPrice":agg["avg_order_price"]["value"],
                "totalOrders":agg["total_orders"]["value"]
            }
            for agg in results["aggregations"]["customer_stats"]["buckets"]
        ]

        return customer_stats

    except Exception as error:
        print(f"Elasticserach query error : {error}")
        raise error
    
@mutation.field("createOrder")
async def resolve_createOrder(_,info,order_id,customer_id,customer_full_name,taxful_total_price, order_date):
    try:
        new_order={
            "order_id":order_id,
            "customer_id":customer_id,
            "customer_full_name":customer_full_name,
            "taxful_total_price":taxful_total_price,
            "order_date":order_date

        }
        es.index(index="kibana_sample_data_ecommerce",document=new_order)

          # Publish the new order to Redis
        await initialize_broadcast()
        await broadcast.publish(channel="orders", message=json.dumps(new_order))
        print(f"Published order: {new_order}")
        # await broadcast.disconnect()

        return new_order


    except Exception as error:
        print(f"Elasticserach query error : {error}")
        raise error
    

@mutation.field("updateOrder")
def resolve_updateOrder(_, info, order_id, customer_id=None, customer_full_name=None, taxful_total_price=None, order_date=None):
    try:
        # Search for the document by order_id
        search_result = es.search(
            index="kibana_sample_data_ecommerce",
            body={
                "query": {
                    "term": {
                        "order_id": order_id
                    }
                }
            }
        )
        
        # Check if the document was found
        if not search_result["hits"]["hits"]:
            raise Exception(f"Order with order_id {order_id} not found.")
        
        # Get the document ID
        doc_id = search_result["hits"]["hits"][0]["_id"]

        # Prepare the script for the partial update
        script = []
        params = {}
        if customer_id is not None:
            script.append("ctx._source.customer_id = params.customer_id;")
            params["customer_id"] = customer_id
        if customer_full_name is not None:
            script.append("ctx._source.customer_full_name = params.customer_full_name;")
            params["customer_full_name"] = customer_full_name
        if taxful_total_price is not None:
            script.append("ctx._source.taxful_total_price = params.taxful_total_price;")
            params["taxful_total_price"] = taxful_total_price
        if order_date is not None:
            script.append("ctx._source.order_date = params.order_date;")
            params["order_date"] = order_date

        # If no fields to update, return an error
        if not script:
            raise Exception("No fields provided to update.")

        # Combine the script into a single string
        script_str = " ".join(script)

        # Execute the update API
        es.update(
            index="kibana_sample_data_ecommerce",
            id=doc_id,
            body={
                "script": {
                    "source": script_str,
                    "lang": "painless",
                    "params": params
                }
            }
        )

        # Fetch the updated document
        updated_doc = es.get(index="kibana_sample_data_ecommerce", id=doc_id)
        updated_order = updated_doc["_source"]

        return updated_order

    except Exception as error:
        print(f"Elasticsearch query error: {error}")
        raise error

@subscription.source("orderCreated")
async def order_created_generator(obj, info):
    print("new order created")
    # await broadcast.connect()
    await initialize_broadcast()
    async with broadcast.subscribe(channel="orders") as subscriber:
        async for event in subscriber:
            order_data = json.loads(event.message)
            yield order_data

@subscription.field("orderCreated")
async def resolve_order_created(order, info):
    return order
