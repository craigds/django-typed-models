from typing import TYPE_CHECKING, Generic

from django.contrib.admin import ModelAdmin

from .models import TypedModel, TypedModelT

if TYPE_CHECKING:
    from django.forms.forms import BaseForm
    from django.http import HttpRequest


class TypedModelAdmin(ModelAdmin, Generic[TypedModelT]):
    model: "type[TypedModelT]"

    def get_fields(
        self,
        request: "HttpRequest",
        obj: "TypedModelT | None" = None,
    ) -> list[str | list[str] | tuple[str, ...]]:
        fields = list(super().get_fields(request, obj))
        # we remove the type field from the admin of subclasses.
        if TypedModel not in self.model.__bases__:
            fields.remove(self.model._meta.get_field("type").name)
        return fields

    def save_model(
        self,
        request: "HttpRequest",
        obj: "TypedModelT",
        form: "BaseForm",
        change,
    ) -> None:
        if getattr(obj, "_typedmodels_type", None) is None:
            # new instances don't have the type attribute
            obj._typedmodels_type = form.cleaned_data["type"]  # type: ignore[misc]
        obj.save()
