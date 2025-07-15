from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review

@receiver(post_save, sender=Review)
def update_Proudct_rating(sender, instance, **kwargs):
    if instance.product:
        instance.product.save()