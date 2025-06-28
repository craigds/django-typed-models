from typing import TYPE_CHECKING, Optional, Sequence, Callable, Any, Generic, Type

from django.contrib.admin import ModelAdmin

from .models import TypedModel, TypedModelT

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.forms.forms import BaseForm


class TypedModelAdmin(ModelAdmin, Generic[TypedModelT]):
    model: "Type[TypedModelT]"
    
    def get_fields(
        self,
        request: "HttpRequest",
        obj: "Optional[TypedModelT]" = None,
    ) -> Sequence[str | Sequence[str]]:
        fields = super().get_fields(request, obj)
        # we remove the type field from the admin of subclasses.
        if TypedModel not in self.model.__bases__:
            fields = list(fields)  # Convert to mutable list
            fields.remove(self.model._meta.get_field('type').name)
        return fields

    def save_model(
        self,
        request: "HttpRequest",
        obj: "TypedModelT",
        form: "BaseForm",
        change,
    ) -> None:
        if getattr(obj, '_typedmodels_type', None) is None:
            # new instances don't have the type attribute
            setattr(obj, '_typedmodels_type', form.cleaned_data['type'])
        obj.save()
