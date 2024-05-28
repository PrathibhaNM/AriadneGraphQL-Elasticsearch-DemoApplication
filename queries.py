
def get_orders_by_customer(customer_id):
    return {
        "query": {
            "term": {
                "customer_id": customer_id
            }
        }
    }

def get_customerstats_BasedOnCategory(category):
    return{
        "size":0,
        "query":{
            "match":{
                "category":category
            }
        },
            "aggs":{
                "customer_stats":{
                    "terms":{
                        "field":"customer_id",
                        "size":10
                    },

                    "aggs":{
                        "avg_order_price":{
                            "avg":{
                                "field":"taxful_total_price"
                            }
                        },

                        "total_orders":{
                            "cardinality": {
                                "field":"order_id"
                            }

                        }
                    }
                }

            }
        
    }
