import time
import uuid

import pytest
from django.apps import apps
from django.db import connection, models

from core.models import BaseModel


@pytest.fixture
def sample_model(transactional_db):
    class SampleModel(BaseModel):
        name = models.CharField(max_length=50)

        class Meta:
            app_label = "core"

    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(SampleModel)
    yield SampleModel
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(SampleModel)
    apps.all_models["core"].pop("samplemodel", None)
    apps.clear_cache()


@pytest.mark.django_db
def test_base_model_fields(sample_model):
    obj = sample_model.objects.create(name="test")
    assert isinstance(obj.id, uuid.UUID)
    assert obj.created_at is not None
    assert obj.updated_at is not None


@pytest.mark.django_db
def test_save_updates_updated_at(sample_model):
    obj = sample_model.objects.create(name="test")
    old_updated_at = obj.updated_at
    time.sleep(0.01)
    obj.save()
    assert obj.updated_at > old_updated_at


@pytest.mark.django_db
def test_str_representation(sample_model):
    obj = sample_model.objects.create(name="test")
    assert str(obj) == f"SampleModel (id: {obj.id})"
