from models import models as models
import psycopg2

db_name = "cj_6_7"
host_name = "localhost"
queries = {
    'get_live_subscriptions': "SELECT st.name, s.customer_id, s.status, s.autorenew, s.start_date, s.end_date, s.is_test, s.id  FROM Subscription s INNER JOIN Store st ON s.store_id = st.id where s.is_test = false",
    'get_live_orders': "SELECT o.placed_at, o.status, o.financial_status, o.fulfillment_status, o.is_test, o.total, o.is_renewal, o.id, som.subscription_id FROM \"order\" o INNER JOIN subscription_order_map som ON som.order_id = o.id where o.is_test = false",
    'get_subscription_logs': "SELECT created_at, log_type, subscription_id FROM Subscription_Log",
    'get_subscription_order_maps': "SELECT * FROM Subscription_Order_Map"
    }

def get_live_subscriptions():
    results = []
    for row in run_query(queries['get_live_subscriptions']):
        sub = models.Subscription(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) 
        results.append(sub)
    return results

def get_live_orders():
    results = []
    for row in run_query(queries['get_live_orders']):
        ord = models.Order(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        results.append(ord)
    return results

def get_subscription_logs():
    results = []
    for row in run_query(queries['get_subscription_logs']):
        log = models.SubscriptionLog(row[0], row[1], row[2])
        results.append(log)
    return results

def get_connection(): 
    return psycopg2.connect("dbname='{}' host='{}'".format(db_name, host_name))

def run_query(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()

