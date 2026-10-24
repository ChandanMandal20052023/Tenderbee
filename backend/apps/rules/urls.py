"""
URL endpoints for RulePack review, modification, and freezing.
"""
from django.urls import path
from apps.rules.views import (
    RuleItemUpdateAPIView,
    RulePackDetailAPIView,
    RulePackFreezeAPIView,
    RulePackListAPIView,
)

app_name = "rules"

urlpatterns = [
    path("", RulePackListAPIView.as_view(), name="rulepack-list"),
    path("<str:rule_pack_id>/", RulePackDetailAPIView.as_view(), name="rulepack-detail"),
    path("<str:rule_pack_id>/confirm/", RulePackFreezeAPIView.as_view(), name="rulepack-confirm"),
    path("<str:rule_pack_id>/items/<str:item_id>/", RuleItemUpdateAPIView.as_view(), name="ruleitem-update"),
]
