from django.contrib.contenttypes.models import ContentType
from django.db import models

import pytest

try:
    import yaml

    PYYAML_AVAILABLE = True
    del yaml
except ImportError:
    PYYAML_AVAILABLE = False

from django.core import serializers
from django.core.exceptions import FieldError

from .models import TypedModelManager
from testapp.models import (
    AngryBigCat,
    Animal,
    BigCat,
    Canine,
    Feline,
    Parrot,
    AbstractVegetable,
    Vegetable,
    Fruit,
    UniqueIdentifier,
    Child2,
)


@pytest.fixture
def animals(db):
    kitteh = Feline.objects.create(name="kitteh")
    UniqueIdentifier.objects.create(
        name="kitteh",
        object_id=kitteh.pk,
        content_type=ContentType.objects.get_for_model(kitteh),
    )
    cheetah = Feline.objects.create(name="cheetah")
    UniqueIdentifier.objects.create(
        name="cheetah",
        object_id=cheetah.pk,
        content_type=ContentType.objects.get_for_model(cheetah),
    )
    fido = Canine.objects.create(name="fido")
    UniqueIdentifier.objects.create(
        name="fido",
        object_id=fido.pk,
        content_type=ContentType.objects.get_for_model(fido),
    )
    simba = BigCat.objects.create(name="simba")
    UniqueIdentifier.objects.create(
        name="simba",
        object_id=simba.pk,
        content_type=ContentType.objects.get_for_model(simba),
    )
    mufasa = AngryBigCat.objects.create(name="mufasa")
    UniqueIdentifier.objects.create(
        name="mufasa",
        object_id=mufasa.pk,
        content_type=ContentType.objects.get_for_model(mufasa),
    )
    kajtek = Parrot.objects.create(name="Kajtek")
    UniqueIdentifier.objects.create(
        name="kajtek",
        object_id=kajtek.pk,
        content_type=ContentType.objects.get_for_model(kajtek),
    )


def test_can_instantiate_base_model(db):
    # direct instantiation works fine without a type, as long as you don't save
    animal = Animal()
    assert not animal.type
    assert type(animal) is Animal


def test_cant_save_untyped_base_model(db):
    # direct instantiation shouldn't work
    with pytest.raises(RuntimeError):
        Animal.objects.create(name="uhoh")

    # ... unless a type is specified
    Animal.objects.create(name="dingo", type="testapp.canine")

    # ... unless that type is stupid
    with pytest.raises(ValueError):
        Animal.objects.create(name="dingo", type="macaroni.buffaloes")


def test_get_types():
    assert set(Animal.get_types()) == {
        "testapp.canine",
        "testapp.bigcat",
        "testapp.parrot",
        "testapp.angrybigcat",
        "testapp.feline",
    }
    assert set(Canine.get_types()) == {"testapp.canine"}
    assert set(Feline.get_types()) == {
        "testapp.bigcat",
        "testapp.angrybigcat",
        "testapp.feline",
    }


def test_get_type_classes():
    assert set(Animal.get_type_classes()) == {
        Canine,
        BigCat,
        Parrot,
        AngryBigCat,
        Feline,
    }
    assert set(Canine.get_type_classes()) == {Canine}
    assert set(Feline.get_type_classes()) == {BigCat, AngryBigCat, Feline}


def test_type_choices():
    type_choices = {cls for cls, _ in Animal._meta.get_field("type").choices}
    assert type_choices == set(Animal.get_types())


def test_base_model_queryset(animals):
    # all objects returned
    qs = Animal.objects.all().order_by("type")
    assert [obj.type for obj in qs] == [
        "testapp.angrybigcat",
        "testapp.bigcat",
        "testapp.canine",
        "testapp.feline",
        "testapp.feline",
        "testapp.parrot",
    ]
    assert [type(obj) for obj in qs] == [
        AngryBigCat,
        BigCat,
        Canine,
        Feline,
        Feline,
        Parrot,
    ]


def test_proxy_model_queryset(animals):
    qs = Canine.objects.all().order_by("type")
    assert qs.count() == 1
    assert len(qs) == 1
    assert [obj.type for obj in qs] == ["testapp.canine"]
    assert [type(obj) for obj in qs] == [Canine]

    qs = Feline.objects.all().order_by("type")
    assert qs.count() == 4
    assert len(qs) == 4
    assert [obj.type for obj in qs] == [
        "testapp.angrybigcat",
        "testapp.bigcat",
        "testapp.feline",
        "testapp.feline",
    ]
    assert [type(obj) for obj in qs] == [AngryBigCat, BigCat, Feline, Feline]


def test_doubly_proxied_model_queryset(animals):
    qs = BigCat.objects.all().order_by("type")
    assert qs.count() == 2
    assert len(qs) == 2
    assert [obj.type for obj in qs] == ["testapp.angrybigcat", "testapp.bigcat"]
    assert [type(obj) for obj in qs] == [AngryBigCat, BigCat]


def test_triply_proxied_model_queryset(animals):
    qs = AngryBigCat.objects.all().order_by("type")
    assert qs.count() == 1
    assert len(qs) == 1
    assert [obj.type for obj in qs] == ["testapp.angrybigcat"]
    assert [type(obj) for obj in qs] == [AngryBigCat]


def test_recast_auto(animals):
    cat = Feline.objects.get(name="kitteh")
    cat.type = "testapp.bigcat"
    cat.recast()
    assert cat.type == "testapp.bigcat"
    assert type(cat) == BigCat


def test_recast_string(animals):
    cat = Feline.objects.get(name="kitteh")
    cat.recast("testapp.bigcat")
    assert cat.type == "testapp.bigcat"
    assert type(cat) == BigCat


def test_recast_modelclass(animals):
    cat = Feline.objects.get(name="kitteh")
    cat.recast(BigCat)
    assert cat.type == "testapp.bigcat"
    assert type(cat) == BigCat


def test_recast_fail(animals):
    cat = Feline.objects.get(name="kitteh")
    with pytest.raises(ValueError):
        cat.recast(AbstractVegetable)
    with pytest.raises(ValueError):
        cat.recast("typedmodels.abstractvegetable")
    with pytest.raises(ValueError):
        cat.recast(Vegetable)
    with pytest.raises(ValueError):
        cat.recast("typedmodels.vegetable")


def test_fields_in_subclasses(animals):
    canine = Canine.objects.all()[0]
    angry = AngryBigCat.objects.all()[0]

    angry.mice_eaten = 5
    angry.save()
    assert AngryBigCat.objects.get(pk=angry.pk).mice_eaten == 5

    angry.canines_eaten.add(canine)
    assert list(angry.canines_eaten.all()) == [canine]

    # Feline class was created before Parrot and has mice_eaten field which is non-m2m, so it may break accessing
    # known_words field in Parrot instances (since Django 1.5).
    parrot = Parrot.objects.all()[0]
    parrot.known_words = 500
    parrot.save()
    assert Parrot.objects.get(pk=parrot.pk).known_words == 500


def test_fields_cache():
    mice_eaten = Feline._meta.get_field("mice_eaten")
    known_words = Parrot._meta.get_field("known_words")
    assert mice_eaten in AngryBigCat._meta.fields
    assert mice_eaten in Feline._meta.fields
    assert mice_eaten not in Parrot._meta.fields
    assert known_words in Parrot._meta.fields
    assert known_words not in AngryBigCat._meta.fields
    assert known_words not in Feline._meta.fields


def test_m2m_cache():
    canines_eaten = AngryBigCat._meta.get_field("canines_eaten")
    assert canines_eaten in AngryBigCat._meta.many_to_many
    assert canines_eaten not in Feline._meta.many_to_many
    assert canines_eaten not in Parrot._meta.many_to_many


def test_related_names(animals):
    """Ensure that accessor names for reverse relations are generated properly."""

    canine = Canine.objects.all()[0]
    assert hasattr(canine, "angrybigcat_set")


def test_queryset_defer(db):
    """
    Ensure that qs.defer() works correctly
    """
    Vegetable.objects.create(name="cauliflower", color="white", yumness=1)
    Vegetable.objects.create(name="spinach", color="green", yumness=5)
    Vegetable.objects.create(name="sweetcorn", color="yellow", yumness=10)
    Fruit.objects.create(name="Apple", color="red", yumness=7)

    qs = AbstractVegetable.objects.defer("yumness")

    objs = set(qs)
    for o in objs:
        assert isinstance(o, AbstractVegetable)
        assert set(o.get_deferred_fields()) == {"yumness"}
        # does a query, since this field was deferred
        assert isinstance(o.yumness, float)


def test_queryset_defer_type(db):
    Vegetable.objects.create(name="cauliflower", color="white", yumness=1)
    Fruit.objects.create(name="Apple", color="red", yumness=7)

    qs = AbstractVegetable.objects.only("id")
    assert len(qs) == 2
    assert type(qs[0]) is AbstractVegetable
    assert type(qs[1]) is AbstractVegetable

    qs = Vegetable.objects.only("id")
    assert len(qs) == 1
    assert type(qs[0]) is Vegetable


def test_queryset_defer_type_with_subclass_fields(db, animals):
    # <relatedQuerySet>.delete() tends to do this .only('id') thing while collating referenced models.
    # So it needs to work even if you think it's a weird thing to do
    # In this case we *don't* auto-cast to anything; all returned models are Animal instances
    # this avoids the following error:
    #     django.core.exceptions.FieldDoesNotExist: AngryBigCat has no field named 'known_words'
    qs = list(Animal.objects.only("id"))
    assert len(qs) == 6
    assert all(type(x) is Animal for x in qs)


@pytest.mark.parametrize(
    "fmt",
    [
        "xml",
        "json",
        pytest.param(
            "yaml",
            marks=[
                pytest.mark.skipif(
                    not PYYAML_AVAILABLE, reason="PyYAML is not available"
                )
            ],
        ),
    ],
)
def test_serialization(fmt, animals):
    """Helper function used to check serialization and deserialization for concrete format."""
    animals = Animal.objects.order_by("pk")
    serialized_animals = serializers.serialize(fmt, animals)
    deserialized_animals = [
        wrapper.object for wrapper in serializers.deserialize(fmt, serialized_animals)
    ]
    assert set(deserialized_animals) == set(animals)


def test_generic_relation(animals):
    for animal in Animal.objects.all():
        assert hasattr(animal, "unique_identifiers")
        assert animal.unique_identifiers.all()

    Feline._meta.get_field("unique_identifiers")
    for feline in Feline.objects.all():
        assert hasattr(feline, "unique_identifiers")
        assert feline.unique_identifiers.all()

    for uid in UniqueIdentifier.objects.all():
        cls = uid.referent.__class__
        animal = cls.objects.filter(unique_identifiers=uid)
        assert isinstance(animal.first(), Animal)

    for uid in UniqueIdentifier.objects.all():
        cls = uid.referent.__class__
        animal = cls.objects.filter(unique_identifiers__name=uid.name)
        assert isinstance(animal.first(), Animal)


def test_manager_classes():
    assert isinstance(Animal.objects, TypedModelManager)
    assert isinstance(Feline.objects, TypedModelManager)
    assert isinstance(BigCat.objects, TypedModelManager)

    # This one has a custom manager defined, but that shouldn't prevent objects from working
    assert isinstance(AbstractVegetable.mymanager, models.Manager)
    assert isinstance(AbstractVegetable.objects, TypedModelManager)

    # subclasses work the same way
    assert isinstance(Vegetable.mymanager, models.Manager)
    assert isinstance(Vegetable.objects, TypedModelManager)


def test_uniqueness_check_on_child(db):
    child2 = Child2.objects.create(a="a")

    # Regression test for https://github.com/craigds/django-typed-models/issues/42
    # FieldDoesNotExist: Child2 has no field named 'b'
    child2.validate_unique()


def test_non_nullable_subclass_field_error():
    with pytest.raises(FieldError):

        class Bug(Animal):
            # should have null=True
            num_legs = models.PositiveIntegerField()


def test_explicit_recast_with_class_on_untyped_instance():
    animal = Animal()
    assert not animal.type
    animal.recast(Feline)
    assert animal.type == "testapp.feline"
    assert type(animal) is Feline


def test_explicit_recast_with_string_on_untyped_instance():
    animal = Animal()
    assert not animal.type
    animal.recast("testapp.feline")
    assert animal.type == "testapp.feline"
    assert type(animal) is Feline
