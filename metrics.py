import models.models as models
import handlers.data_grabber as dg
import handlers.metric_maker as mm
import sys
import getopt

def main(argv):
    subs = dg.get_live_subscriptions()
    orders = dg.get_live_orders()
    logs = dg.get_subscription_logs()
    store_metrics = mm.create_metrics(subs, orders, logs)
    has_args = len(argv) > 0

    def store_name_in_args(store_name, args):
        if any([arg for arg in args if arg.lower() in store_metric.store_name.lower()]):
            return True
        return False
                

    for store_metric in store_metrics:
        if not 'all' in argv and store_metric.store_name != 'All' and has_args and not store_name_in_args(store_metric.store_name, argv):
            continue
        metrics_by_month = mm.get_monthly_metrics_for_store(store_metric)
        if not any([metric for metric in metrics_by_month if metric.total_subs > 10]):
            continue
        print store_metric.store_name
        for metric in metrics_by_month:
            if metric.total_subs < 10:
                continue
            print "Month: #{}, Sub Growth: {}%, Added: {}, Lost: {}, Total: {}, Gross Income: ${}".\
                format(metric.month, metric.percent_growth, metric.subs_added, metric.subs_lost, metric.total_subs, metric.gross_income)

if __name__ == "__main__":
    main(sys.argv[1:])
