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

query = QueryType()
mutation=MutationType()
subscription=SubscriptionType()

#Query resolver to get the orders of the customer
@query.field("ordersByCustomer")
def resolve_orders_by_customer(_, info, customerId):
   
    
    try:
        
        # query_body = get_orders_by_customer(customerId)
        # print(query_body)
        
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
        # print(orders)
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
def resolve_createOrder(_,info,order_id,customer_id,customer_full_name,taxful_total_price, order_date):
    try:
        new_order={
            "order_id":order_id,
            "customer_id":customer_id,
            "customer_full_name":customer_full_name,
            "taxful_total_price":taxful_total_price,
            "order_date":order_date

        }
        es.index(index="kibana_sample_data_ecommerce",document=new_order)
        return new_order


    except Exception as error:
        print(f"Elasticserach query error : {error}")
        raise error
    
# @mutation.field("updateOrder")
# def resolve_updateOrder(_, info, order_id, customer_id=None, customer_full_name=None, taxful_total_price=None, order_date=None):
#     try:
#         # Search for the document by order_id
#         search_result = es.search(
#             index="kibana_sample_data_ecommerce",
#             body={
#                 "query": {
#                     "term": {
#                         "order_id": order_id
#                     }
#                 }
#             }
#         )
        
#         # Check if the document was found
#         if not search_result["hits"]["hits"]:
#             raise Exception(f"Order with order_id {order_id} not found.")
        
#         # Get the document ID and source
#         doc_id = search_result["hits"]["hits"][0]["_id"]
#         order = search_result["hits"]["hits"][0]["_source"]

#         # Update fields if new values are provided
#         if customer_id is not None:
#             order["customer_id"] = customer_id
#         if customer_full_name is not None:
#             order["customer_full_name"] = customer_full_name
#         if taxful_total_price is not None:
#             order["taxful_total_price"] = taxful_total_price
#         if order_date is not None:
#             order["order_date"] = order_date

#         # Index the updated order document
#         es.index(index="kibana_sample_data_ecommerce", id=doc_id, document=order)
#         return order

#     except Exception as error:
#         print(f"Elasticsearch query error: {error}")
#         raise error

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

async def fetch_orders():
    
    try:
        now = datetime.now() 
        query_body = {
            "query": {
                "range": {
                    "order_date": {
                        "lte": now,
                        "gte": now-timedelta(days=1)
                    }
                }
            },
            "size": 10  # Adjust batch size as needed
        }

        scrollData = es.search(
            index="kibana_sample_data_ecommerce",
            body=query_body,
            scroll="1m"  # Scroll timeout
        )

        while True:
            # Extract hits from the scroll response
            hits = scrollData["hits"]["hits"]
            if not hits:
                break
            
            orders_chunk = [
                {
                    "order_id": hit["_source"]["order_id"],
                    "customer_id": hit["_source"]["customer_id"],
                    "customer_full_name": hit["_source"]["customer_full_name"],
                    "taxful_total_price": hit["_source"]["taxful_total_price"],
                    "order_date": hit["_source"]["order_date"]
                }
                for hit in hits
            ]

            message = json.dumps({"orders": orders_chunk})
            print("Publishing orders_chunk to Redis:", message) 
            await broadcast.publish("orders_channel", message)
           
            
            scroll_id = scrollData["_scroll_id"]
            scrollData = es.scroll(scroll_id=scroll_id, scroll="1m")
            await asyncio.sleep(2)

        # await queue.put(None)

    except Exception as error:
        print(f"ElasticSerach query error: {error}")
        raise error
    
@subscription.source("ordersLastDay")
async def orders_last_day_generator(obj,info):
    print("In the subscription source")
    asyncio.create_task(fetch_orders())
     
    async with broadcast.subscribe("orders_channel") as subscriber:
        async for event in subscriber:
           print("Received event from Redis:", event.message) 
           message = json.loads(event.message)
           yield message["orders"]
        
       

@subscription.field("ordersLastDay")
async def resolve_orders_last_month(orders, info):
    # Return the orders fetched from the subscription source
    return orders

async def start_broadcast():
    print("-----------")
    await broadcast.connect()

async def stop_broadcast():
    await broadcast.disconnect()





