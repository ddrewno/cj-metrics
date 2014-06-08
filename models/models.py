import psycopg2
import json
import operator


class Subscription:
    def __init__(self, store_name, customer_id, status, autorenew, start_date, end_date, is_test, id, Orders=None, Logs=None):
        self.id = id
        self.store_name = store_name
        self.customer_id = customer_id
        self.status = status
        self.autorenew = autorenew
        self.start_date = start_date
        self.end_date = end_date
        self.is_test = is_test

   
    @property
    def when_started(self):
        return self.start_date
        first_started = None
        for log in [log for log in self.logs if log.log_type == 2]:
            if not first_started or log.created_at < first_started.created_at:
                first_started = log
        return first_started.created_at if first_started else self.start_date
        
    @property
    def when_stopped(self):
        last_entry = None
        for log in self.logs:
            if not last_entry or log.created_at > last_entry.created_at:
                last_entry = log

        return last_entry.created_at if last_entry and last_entry.log_type > 3 else None

    @property
    def first_order_start(self):
        first_order = None
        for order in self.orders:
            if not first_order or order.placed_at < first_order.placed_at:
                first_order = order
        return first_order.placed_at

    @property 
    def duration_active(self):
        start_time = self.when_started
        q
        end_time = self.when_stopped
        return (end_time - start_time).days if end_time else 999999

    @property 
    def months_active(self):
        start_month = self.when_started.year * 12 + self.when_started.month
        end_month = self.when_stopped.year * 12 + self.when_stopped.month + 1 if self.when_stopped else None

        return end_month - start_month if end_month else 999

class SubscriptionLog:
    def __init__(self, created_at, log_type, subscription_id):
        self.created_at = created_at
        self.log_type = log_type
        self.subscription_id = subscription_id

    @property
    def unique_month(self):
        return self.created_at.year * 12 + self.created_at.month

class Order:
    def __init__(self, placed_at, status, financial_status, fulfillment_status, is_test, total, is_renewal, id, subscription_id):
        self.placed_at = placed_at
        self.status = status
        self.financial_status = financial_status
        self.fulfillment_status = fulfillment_status
        self.is_test = is_test
        self.total = total
        self.is_renewal = is_renewal
        self.id = id
        self.subscription_id = subscription_id

    @property
    def unique_month(self):
        return self.placed_at.year * 12 + self.placed_at.month

class StoreMetric:
    def __init__(self, store_name, Subscriptions, Orders, SubscriptionLogs):
        self.store_name = store_name
        self.subscriptions = Subscriptions
        self.orders = Orders
        self.subscription_logs = SubscriptionLogs
        self.monthly_metrics = []

class Metric:
    def __init__(self, month, subs_added, subs_lost, total_subs, gross_income):
        self.month = month
        self.subs_added = subs_added
        self.subs_lost = subs_lost
        self.total_subs = total_subs
        self.gross_income = gross_income

    @property
    def percent_growth(self):
        monthly_growth = self.subs_added - self.subs_lost
        denominator = self.total_subs - monthly_growth
        
        return int(float(monthly_growth) * 100 / (float(denominator))) if denominator != 0 else 'inf' 

    @property
    def percent_retention(self):
        monthly_start = self.total_subs - self.subs_added + self.subs_lost
        return int(float(self.total_subs - self.subs_added) * 100 / (float(monthly_start))) if monthly_start != 0 else 'inf'

       
