from django.test import TestCase
from unittest.mock import MagicMock, call, patch

from django.contrib.contenttypes.models import ContentType
from django.db import models
from translation.exceptions import (
    ContentTypeDoesNotExistError,
    InvalidContentTypeIDError,
    InvalidInstanceFieldIDError,
    ModelInstanceDoesNotExistError
)
from translation.field_ids import (
    build_instance_field_id,
    parse_instance_field_id,
    _build_content_type_id,
    _parse_content_type_id
)

class TestModel(models.Model):
    class Meta:
        app_label = 'contenttranslationtools'
        managed = False

    test_model_field = models.CharField(max_length=100)

class TestFieldIdWithValidInstance(TestCase):
    def setUp(self):
        self.instance = TestModel(id=1)

        self.content_type = MagicMock()
        self.content_type.app_label = 'contenttranslationtools'
        self.content_type.model = 'testmodel'
        self.content_type.model_class.return_value = TestModel

    def test_build_instance_field_id(self):
        instance_field_id = build_instance_field_id(self.instance, 'test_model_field')
        self.assertEqual(instance_field_id, 'contenttranslationtools.testmodel@test_model_field@1')

    def test_build_instance_field_id_with_any_field(self):
        instance_field_id = build_instance_field_id(self.instance, 'not_a_test_model_field')
        self.assertEqual(instance_field_id, 'contenttranslationtools.testmodel@not_a_test_model_field@1')

    def test_parse_instance_field_id(self):
        with patch('translation.field_ids._parse_content_type_id') as parse_content_type_id:
            parse_content_type_id.return_value = self.content_type

            with patch.object(TestModel.objects, 'get') as test_model_get:
                test_model_get.return_value = self.instance

                result = parse_instance_field_id('contenttranslationtools.testmodel@test_model_field@1')

                parse_content_type_id.assert_called_once_with('contenttranslationtools.testmodel')
                test_model_get.assert_called_once_with(pk='1')

            instance, field_id = result

            self.assertEqual(instance, self.instance)
            self.assertEqual(field_id, 'test_model_field')

    def test_parse_instance_field_id_with_invalid_value_raises_error(self):
        with self.assertRaises(InvalidInstanceFieldIDError):
            parse_instance_field_id('not an instance field id')

    def test_parse_instance_field_id_with_nonexistent_model_raises_error(self):
        content_type = MagicMock()
        content_type.app_label = 'contenttranslationtools'
        content_type.model ='not_a_model'
        content_type.model_class.return_value = None

        with patch('translation.field_ids._parse_content_type_id') as parse_content_type_id:
            parse_content_type_id.return_value = content_type

            with self.assertRaises(ModelInstanceDoesNotExistError):
                parse_instance_field_id('contenttranslationtools.not_a_current_model@some_field@1')

    def test_build_content_type_id(self):
        result = _build_content_type_id(self.content_type)
        self.assertEqual(result, 'contenttranslationtools.testmodel')

    def test_parse_content_type_id(self):
        with patch('translation.field_ids.ContentType.objects.get') as content_type_get:
            content_type_get.return_value = self.content_type

            result = _parse_content_type_id('contenttranslationtools.testmodel')

            content_type_get.assert_called_once_with(app_label='contenttranslationtools', model='testmodel')

        self.assertEqual(result, self.content_type)

    def test_parse_content_type_id_with_invalid_value_raises_error(self):
        with self.assertRaises(InvalidContentTypeIDError):
            _parse_content_type_id('not a content type id')

    def test_parse_content_type_id_with_nonexistent_content_type_raises_error(self):
        with patch('translation.field_ids.ContentType.objects.get') as content_type_get:
            content_type_get.side_effect = ContentType.DoesNotExist()

            with self.assertRaises(ContentTypeDoesNotExistError):
                _parse_content_type_id('contenttranslationtools.not_a_content_type')
