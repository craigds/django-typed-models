from django.test import TestCase

from myapp.models import AngryBigCat, Animal, BigCat, Canine, Feline


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
        Animal.objects.create(name="dingo", type="myapp.canine")

        # ... unless that type is stupid
        try:
            Animal.objects.create(name="dingo", type="macaroni.buffaloes")
        except ValueError:
            pass

    def test_base_model_queryset(self):
        # all objects returned
        qs = Animal.objects.all().order_by('type')
        self.assertEqual(len(qs), 5)
        self.assertEqual([obj.type for obj in qs], ['myapp.angrybigcat', 'myapp.bigcat', 'myapp.canine', 'myapp.feline', 'myapp.feline'])
        self.assertEqual([type(obj) for obj in qs], [AngryBigCat, BigCat, Canine, Feline, Feline])

    def test_proxy_model_queryset(self):
        qs = Canine.objects.all()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(len(qs), 1)
        self.assertEqual([obj.type for obj in qs], ['myapp.canine'])
        self.assertEqual([type(obj) for obj in qs], [Canine])

        qs = Feline.objects.all()
        self.assertEqual(qs.count(), 4)
        self.assertEqual(len(qs), 4)
        self.assertEqual([obj.type for obj in qs], ['myapp.angrybigcat', 'myapp.bigcat', 'myapp.feline', 'myapp.feline'])
        self.assertEqual([type(obj) for obj in qs], [AngryBigCat, BigCat, Feline, Feline])

    def test_doubly_proxied_model_queryset(self):
        qs = BigCat.objects.all()
        self.assertEqual(qs.count(), 2)
        self.assertEqual(len(qs), 2)
        self.assertEqual([obj.type for obj in qs], ['myapp.angrybigcat', 'myapp.bigcat'])
        self.assertEqual([type(obj) for obj in qs], [AngryBigCat, BigCat])

    def test_triply_proxied_model_queryset(self):
        qs = AngryBigCat.objects.all()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(len(qs), 1)
        self.assertEqual([obj.type for obj in qs], ['myapp.angrybigcat'])
        self.assertEqual([type(obj) for obj in qs], [AngryBigCat])
