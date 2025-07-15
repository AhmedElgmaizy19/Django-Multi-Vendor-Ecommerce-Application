from store.models import Notifications

def send_notification(user=None,vendor=None,order=None,order_item=None):
    Notifications.objects.create(
        user=user,
        vendor=vendor,
        order=order,
        order_item=order_item,
    )