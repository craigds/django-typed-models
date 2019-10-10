from django.contrib import admin
from .models import TypedModel

class TypedModelAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # we remove the type field from the admin of subclasses.
        if TypedModel not in self.model.__bases__:
            fields.remove(self.model._meta.get_field('type').name)
        return fields

    def save_model(self, request, obj, form, change):
        if getattr(obj, '_typedmodels_type', None) is None:
            # new instances don't have the type attribute
            obj._typedmodels_type = form.cleaned_data['type']
        obj.save()
