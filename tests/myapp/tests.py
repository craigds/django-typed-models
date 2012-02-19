from django.test import TestCase

from myapp.models import Animal, BigCat, Canine, Feline


class SetupStuff(TestCase):
    def setUp(self):
        Feline.objects.create(name="kitteh")
        Feline.objects.create(name="cheetah")
        Canine.objects.create(name="fido")
        BigCat.objects.create(name="simba")


class TestTypedModels(SetupStuff):
    def test_cant_instantiate_base_model(self):
        # direct instantiation shouldn't work
        self.assertRaises(RuntimeError, Animal.objects.create, name="uhoh")

        # ... unless a type is specified
        Animal.objects.create(name="dingo", type="myapp.canine")

        # ... unless that type is stupid
        try:
            Animal.objects.create(name="dingo", type="macaroni.buffaloes")
        except ValueError:
            pass

    def test_base_model_queryset(self):
        # all objects returned
        qs = Animal.objects.all().order_by('type')
        self.assertEqual(len(qs), 4)
        self.assertEqual([obj.type for obj in qs], ['myapp.bigcat', 'myapp.canine', 'myapp.feline', 'myapp.feline'])
        self.assertEqual([type(obj) for obj in qs], [BigCat, Canine, Feline, Feline])

    def test_proxy_model_queryset(self):
        qs = Canine.objects.all()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(len(qs), 1)
        self.assertEqual([obj.type for obj in qs], ['myapp.canine'])
        self.assertEqual([type(obj) for obj in qs], [Canine])

        qs = Feline.objects.all()
        self.assertEqual(qs.count(), 3)
        self.assertEqual(len(qs), 3)
        self.assertEqual([obj.type for obj in qs], ['myapp.bigcat', 'myapp.feline', 'myapp.feline'])
        self.assertEqual([type(obj) for obj in qs], [BigCat, Feline, Feline])

    def test_doubly_proxied_model_queryset(self):
        qs = BigCat.objects.all()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(len(qs), 1)
        self.assertEqual([obj.type for obj in qs], ['myapp.bigcat'])
        self.assertEqual([type(obj) for obj in qs], [BigCat])
