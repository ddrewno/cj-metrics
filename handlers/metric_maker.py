from models import models as models

def create_metrics(Subscriptions, Orders, SubscriptionLogs):
    ret = []
    metric_dict = {}
    subs_to_stores = {}

    for sub in Subscriptions:
        name = sub.store_name
        if name not in metric_dict:
            metric_dict[name] = {
                    'subscriptions':[],
                    'orders': [],
                    'subscription_logs': []
                    }
        metric_dict[name]['subscriptions'].append(sub)
        subs_to_stores[sub.id] = name

    for ord in Orders: 
        if ord.subscription_id in subs_to_stores:
            name = subs_to_stores[ord.subscription_id]
            metric_dict[name]['orders'].append(ord)

    for log in SubscriptionLogs: 
        if log.subscription_id in subs_to_stores:
            name = subs_to_stores[log.subscription_id]
            metric_dict[name]['subscription_logs'].append(log)

    for key in metric_dict:
        store_metric = models.StoreMetric(key, metric_dict[key]['subscriptions'], metric_dict[key]['orders'], metric_dict[key]['subscription_logs'])
        ret.append(store_metric)

    aggregate = {
            'subscriptions': [],
            'orders': [],
            'subscription_logs': []
            }
    for metric in ret:
        if len(metric.subscriptions) < 20:
            continue
        aggregate['subscriptions'].extend(metric.subscriptions)
        aggregate['orders'].extend(metric.orders)
        aggregate['subscription_logs'].extend(metric.subscription_logs)

    aggregate_metric = models.StoreMetric("All", aggregate['subscriptions'], aggregate['orders'], aggregate['subscription_logs'])
    ret.append(aggregate_metric)

    return ret 

def get_monthly_metrics_for_store(StoreMetric):
    ret = []
    def get_last_order_for_subscription(Subscription, Orders):
        target_id = Subscription.id
        orders = [ ord for ord in Orders if ord.subscription_id == target_id ]
        last_order = None
        for ord in orders:
            if not last_order or ord.placed_at > last_order.placed_at:
                last_order = ord
        
        return last_order
    
    def get_all_orders_by_month(Orders):
        ret = {}
        for ord in [ord for ord in Orders if ord.financial_status == 4]:
            key = ord.unique_month
            if key not in ret: 
                ret[key] = []
            ret[key].append(ord) 
        return ret


    def get_orders_started_by_month(Orders):
        ret = {}
        for ord in [ord for ord in Orders if ord.is_renewal == False and ord.financial_status in (1,2,3,4)]:
            key = ord.unique_month
            if key not in ret: 
                ret[key] = []
            ret[key].append(ord) 
        return ret

    def get_orders_stopped_by_month(Orders, Subscriptions, Logs):
        ret = {}
        sub_end_dates = {}

        # Check each sub to see if its last log entry was a failure (aka no longer active)
        for sub in Subscriptions:
            last_log = None
            for log in [log for log in Logs if log.subscription_id == sub.id]:
                if not last_log or log.created_at > last_log.created_at:
                    last_log = log

            if last_log.log_type in (4,5,6): 
                last_order = get_last_order_for_subscription(sub, Orders)
                key = last_order.unique_month
                # if someone ordered and canceled in the same month - count as next month's cancellation
                if last_log.unique_month == last_order.unique_month:
                    key += 1
                if key not in ret:
                    ret[key] = []
                ret[key].append(last_order)
        
        return ret

    monthly_orders_started = get_orders_started_by_month(StoreMetric.orders) 
    monthly_orders_all = get_all_orders_by_month(StoreMetric.orders) 
    monthly_orders_stopped = get_orders_stopped_by_month(StoreMetric.orders, StoreMetric.subscriptions, StoreMetric.subscription_logs)

    # at this point months are large numbers (year * 12 + month #). Normalize this to go from 1->inf
    first_month = None 
    for key in monthly_orders_all: 
        if not first_month or key < first_month:
            first_month = key

    ret = []
    subs_running_total = 0

    while len(monthly_orders_all) > 0:
        lowest_key = None
        for key in monthly_orders_all:
            if not lowest_key or int(key) < int(lowest_key):
                lowest_key = key
        month = int(lowest_key) - int(first_month) + 1
        subs_added = len(monthly_orders_started[lowest_key]) if lowest_key in monthly_orders_started else 0
        subs_lost = len(monthly_orders_stopped[lowest_key]) if lowest_key in monthly_orders_stopped else 0
        subs_running_total = subs_running_total + subs_added - subs_lost
        gross_income = float(sum([ord.total for ord in monthly_orders_all[lowest_key]]))/100 if key in monthly_orders_all else 0
        metric = models.Metric(month, subs_added, subs_lost, subs_running_total, gross_income) 

        ret.append(metric)
        del monthly_orders_all[lowest_key]

    return ret

