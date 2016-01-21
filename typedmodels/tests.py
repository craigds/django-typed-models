import unittest
try:
    import yaml
    PYYAML_AVAILABLE = True
except ImportError:
    PYYAML_AVAILABLE = False

from django.core import serializers
from django.test import TestCase
from django.db.models.query_utils import DeferredAttribute

from .test_models import AngryBigCat, Animal, BigCat, Canine, Feline, Parrot, AbstractVegetable, Vegetable, Fruit


class SetupStuff(TestCase):
    def setUp(self):
        Feline.objects.create(name="kitteh")
        Feline.objects.create(name="cheetah")
        Canine.objects.create(name="fido")
        BigCat.objects.create(name="simba")
        AngryBigCat.objects.create(name="mufasa")
        Parrot.objects.create(name="Kajtek")


class TestTypedModels(SetupStuff):
    def test_cant_instantiate_base_model(self):
        # direct instantiation shouldn't work
        self.assertRaises(RuntimeError, Animal.objects.create, name="uhoh")

        # ... unless a type is specified
        Animal.objects.create(name="dingo", type="typedmodels.canine")

        # ... unless that type is stupid
        try:
            Animal.objects.create(name="dingo", type="macaroni.buffaloes")
        except ValueError:
            pass

    def test_get_types(self):
        self.assertEqual(set(Animal.get_types()), set(['typedmodels.canine', 'typedmodels.bigcat', 'typedmodels.parrot', 'typedmodels.angrybigcat', 'typedmodels.feline']))
        self.assertEqual(set(Canine.get_types()), set(['typedmodels.canine']))
        self.assertEqual(set(Feline.get_types()), set(['typedmodels.bigcat', 'typedmodels.angrybigcat', 'typedmodels.feline']))

    def test_get_type_classes(self):
        self.assertEqual(set(Animal.get_type_classes()), set([Canine, BigCat, Parrot, AngryBigCat, Feline]))
        self.assertEqual(set(Canine.get_type_classes()), set([Canine]))
        self.assertEqual(set(Feline.get_type_classes()), set([BigCat, AngryBigCat, Feline]))

    def test_type_choices(self):
        type_choices = set((cls for cls, _  in Animal._meta.get_field('type').choices))
        self.assertEqual(type_choices, set(Animal.get_types()))

    def test_base_model_queryset(self):
        # all objects returned
        qs = Animal.objects.all().order_by('type')
        self.assertEqual(len(qs), 6)
        self.assertEqual([obj.type for obj in qs], ['typedmodels.angrybigcat', 'typedmodels.bigcat', 'typedmodels.canine', 'typedmodels.feline', 'typedmodels.feline', 'typedmodels.parrot'])
        self.assertEqual([type(obj) for obj in qs], [AngryBigCat, BigCat, Canine, Feline, Feline, Parrot])

    def test_proxy_model_queryset(self):
        qs = Canine.objects.all().order_by('type')
        self.assertEqual(qs.count(), 1)
        self.assertEqual(len(qs), 1)
        self.assertEqual([obj.type for obj in qs], ['typedmodels.canine'])
        self.assertEqual([type(obj) for obj in qs], [Canine])

        qs = Feline.objects.all().order_by('type')
        self.assertEqual(qs.count(), 4)
        self.assertEqual(len(qs), 4)
        self.assertEqual([obj.type for obj in qs], ['typedmodels.angrybigcat', 'typedmodels.bigcat', 'typedmodels.feline', 'typedmodels.feline'])
        self.assertEqual([type(obj) for obj in qs], [AngryBigCat, BigCat, Feline, Feline])

    def test_doubly_proxied_model_queryset(self):
        qs = BigCat.objects.all().order_by('type')
        self.assertEqual(qs.count(), 2)
        self.assertEqual(len(qs), 2)
        self.assertEqual([obj.type for obj in qs], ['typedmodels.angrybigcat', 'typedmodels.bigcat'])
        self.assertEqual([type(obj) for obj in qs], [AngryBigCat, BigCat])

    def test_triply_proxied_model_queryset(self):
        qs = AngryBigCat.objects.all().order_by('type')
        self.assertEqual(qs.count(), 1)
        self.assertEqual(len(qs), 1)
        self.assertEqual([obj.type for obj in qs], ['typedmodels.angrybigcat'])
        self.assertEqual([type(obj) for obj in qs], [AngryBigCat])

    def test_recast_auto(self):
        cat = Feline.objects.get(name='kitteh')
        cat.type = 'typedmodels.bigcat'
        cat.recast()
        self.assertEqual(cat.type, 'typedmodels.bigcat')
        self.assertEqual(type(cat), BigCat)

    def test_recast_string(self):
        cat = Feline.objects.get(name='kitteh')
        cat.recast('typedmodels.bigcat')
        self.assertEqual(cat.type, 'typedmodels.bigcat')
        self.assertEqual(type(cat), BigCat)

    def test_recast_modelclass(self):
        cat = Feline.objects.get(name='kitteh')
        cat.recast(BigCat)
        self.assertEqual(cat.type, 'typedmodels.bigcat')
        self.assertEqual(type(cat), BigCat)

    def test_recast_fail(self):
        cat = Feline.objects.get(name='kitteh')
        self.assertRaises(ValueError, cat.recast, AbstractVegetable)
        self.assertRaises(ValueError, cat.recast, 'typedmodels.abstractvegetable')
        self.assertRaises(ValueError, cat.recast, Vegetable)
        self.assertRaises(ValueError, cat.recast, 'typedmodels.vegetable')

    def test_fields_in_subclasses(self):
        canine = Canine.objects.all()[0]
        angry = AngryBigCat.objects.all()[0]

        angry.mice_eaten = 5
        angry.save()
        self.assertEqual(AngryBigCat.objects.get(pk=angry.pk).mice_eaten, 5)

        angry.canines_eaten.add(canine)
        self.assertEqual(list(angry.canines_eaten.all()), [canine])

        # Feline class was created before Parrot and has mice_eaten field which is non-m2m, so it may break accessing
        # known_words field in Parrot instances (since Django 1.5).
        parrot = Parrot.objects.all()[0]
        parrot.known_words = 500
        parrot.save()
        self.assertEqual(Parrot.objects.get(pk=parrot.pk).known_words, 500)

    def test_fields_cache(self):
        mice_eaten = Feline._meta.get_field('mice_eaten')
        known_words = Parrot._meta.get_field('known_words')
        self.assertIn(mice_eaten, AngryBigCat._meta.fields)
        self.assertIn(mice_eaten, Feline._meta.fields)
        self.assertNotIn(mice_eaten, Parrot._meta.fields)
        self.assertIn(known_words, Parrot._meta.fields)
        self.assertNotIn(known_words, AngryBigCat._meta.fields)
        self.assertNotIn(known_words, Feline._meta.fields)

    def test_m2m_cache(self):
        canines_eaten = AngryBigCat._meta.get_field('canines_eaten')
        self.assertIn(canines_eaten, AngryBigCat._meta.many_to_many)
        self.assertNotIn(canines_eaten, Feline._meta.many_to_many)
        self.assertNotIn(canines_eaten, Parrot._meta.many_to_many)

    def test_related_names(self):
        '''Ensure that accessor names for reverse relations are generated properly.'''

        canine = Canine.objects.all()[0]
        self.assertTrue(hasattr(canine, 'angrybigcat_set'))

    def test_queryset_defer(self):
        """
        Ensure that qs.defer() works correctly
        """
        Vegetable.objects.create(name='cauliflower', color='white', yumness=1)
        Vegetable.objects.create(name='spinach', color='green', yumness=5)
        Vegetable.objects.create(name='sweetcorn', color='yellow', yumness=10)
        Fruit.objects.create(name='Apple', color='red', yumness=7)

        qs = AbstractVegetable.objects.defer('yumness')

        objs = set(qs)
        for o in objs:
            print(o)
            self.assertIsInstance(o, AbstractVegetable)
            self.assertTrue(o._deferred)
            self.assertIsInstance(o.__class__.__dict__['yumness'], DeferredAttribute)
            # does a query, since this field was deferred
            self.assertIsInstance(o.yumness, float)

    def _check_serialization(self, serialization_format):
        """Helper function used to check serialization and deserialization for concrete format."""
        animals = Animal.objects.order_by('pk')
        serialized_animals = serializers.serialize(serialization_format, animals)
        deserialized_animals = [wrapper.object for wrapper in serializers.deserialize(serialization_format, serialized_animals)]
        self.assertEqual(set(deserialized_animals), set(animals))

    def test_xml_serialization(self):
        self._check_serialization('xml')

    def test_json_serialization(self):
        self._check_serialization('json')

    @unittest.skipUnless(PYYAML_AVAILABLE, 'PyYAML is not available.')
    def test_yaml_serialization(self):
        self._check_serialization('yaml')
