from django.test import TestCase

from .test_models import AngryBigCat, Animal, BigCat, Canine, Feline


class SetupStuff(TestCase):
    def setUp(self):
        Feline.objects.create(name="kitteh")
        Feline.objects.create(name="cheetah")
        Canine.objects.create(name="fido")
        BigCat.objects.create(name="simba")
        AngryBigCat.objects.create(name="mufasa")


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

    def test_base_model_queryset(self):
        # all objects returned
        qs = Animal.objects.all().order_by('type')
        self.assertEqual(len(qs), 5)
        self.assertEqual([obj.type for obj in qs], ['typedmodels.angrybigcat', 'typedmodels.bigcat', 'typedmodels.canine', 'typedmodels.feline', 'typedmodels.feline'])
        self.assertEqual([type(obj) for obj in qs], [AngryBigCat, BigCat, Canine, Feline, Feline])

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

    def test_fields_in_subclasses(self):
        canine = Canine.objects.all()[0]
        angry = AngryBigCat.objects.all()[0]

        angry.mice_eaten = 5
        angry.save()
        self.assertEqual(AngryBigCat.objects.get(pk=angry.pk).mice_eaten, 5)
        
        angry.canines_eaten.add(canine)
        self.assertEqual(list(angry.canines_eaten.all()), [canine])

    def test_related_names(self):
        '''Ensure that accessor names for reverse relations are generated properly.'''

        canine = Canine.objects.all()[0]
        self.assertTrue(hasattr(canine, 'angrybigcat_set'))
        

        
