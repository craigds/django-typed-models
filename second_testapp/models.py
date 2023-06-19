from django.db import models

from typedmodels.models import TypedModel


class BaseReview(TypedModel):
    rating = models.IntegerField()
    customer = models.ForeignKey("testapp.Employee", on_delete=models.CASCADE, related_name="reviews", null=True)


class OrderReview(BaseReview):
    product = models.ForeignKey("testapp.Product", on_delete=models.CASCADE, related_name="reviews", null=True)
    order = models.OneToOneField("testapp.Order", on_delete=models.CASCADE, related_name="order_review", null=True)

