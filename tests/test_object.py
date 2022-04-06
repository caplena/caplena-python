import unittest
from datetime import datetime
from typing import Any, Dict, List, Optional

from typing_extensions import Literal

from caplena.constants import NOT_SET
from caplena.endpoints.base_endpoint import BaseController, BaseObject, BaseResource
from caplena.helpers import Helpers
from caplena.list import CaplenaList
from tests.common import common_config


class SomeController(BaseController):
    pass


class SomeObject(BaseResource[SomeController]):
    class SomeNested(BaseObject[SomeController]):
        class Metadata(BaseObject[SomeController]):
            __fields__ = {"some_other_field", "reviewed_count"}
            __mutable__ = {"reviewed_count"}
            some_other_field: int
            reviewed_count: int

        __fields__ = {"ref", "name", "type", "metadata"}
        __mutable__ = {"ref"}
        ref: str
        name: str
        type: Literal["numerical", "boolean", "text", "date", "any", "text_to_analyze"]
        metadata: Metadata

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]) -> "SomeObject.SomeNested":
            obj["metadata"] = cls.Metadata.parse_obj(obj["metadata"])
            return super().parse_obj(obj)

    __fields__ = {
        "name",
        "tags",
        "upload_status",
        "columns",
        "created",
        "last_modified",
        "translation_status",
        "nested",
    }
    __mutable__ = {"name", "tags", "created", "translation_status", "nested"}

    name: str
    tags: List[str]
    upload_status: Literal["pending", "in_progress", "succeeded", "failed"]
    columns: CaplenaList[SomeNested]
    created: datetime
    last_modified: datetime
    translation_status: Optional[str]
    nested: SomeNested

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "SomeObject":
        obj["columns"] = CaplenaList(
            values=[cls.SomeNested.parse_obj(column) for column in obj["columns"]]
        )
        obj["nested"] = cls.SomeNested.parse_obj(obj["nested"])
        obj["created"] = Helpers.from_rfc3339_datetime(obj["created"])
        obj["last_modified"] = Helpers.from_rfc3339_datetime(obj["last_modified"])

        return super().parse_obj(obj)


class CustomizedObject(SomeObject):
    class SomeNested(SomeObject.SomeNested):
        def modified_dict(self) -> Any:
            modified: Any = super().modified_dict()
            if modified == NOT_SET:
                modified = {}

            modified["ref"] = self.ref
            modified["type"] = self.type
            return modified


class BaseObjectTests(unittest.TestCase):
    controller = SomeController(config=common_config)

    def build_object_dict(self) -> Dict[str, Any]:
        return {
            "id": "id_object",
            "name": "Hello",
            "tags": ["tag1", "tag2"],
            "upload_status": "pending",
            "columns": [
                {
                    "ref": "column_1",
                    "name": "Column 1",
                    "type": "numerical",
                    "metadata": {"some_other_field": 12, "reviewed_count": 42},
                },
                {
                    "ref": "column_2",
                    "name": "Column 2",
                    "type": "date",
                    "metadata": {"some_other_field": 400, "reviewed_count": 40000},
                },
            ],
            "created": "2022-03-14T08:18:38.910Z",
            "last_modified": "2021-03-14T08:18:38.905Z",
            "translation_status": None,
            "nested": {
                "ref": "some_ref",
                "name": "nested name",
                "type": "numerical",
                "metadata": {"some_other_field": 12, "reviewed_count": 42},
            },
        }

    def build_obj(self, *, obj_exists: bool = False) -> SomeObject:
        return SomeObject.build_obj(
            self.build_object_dict(), controller=self.controller, obj_exists=obj_exists
        )

    def build_customized(self, *, obj_exists: bool = False) -> CustomizedObject:
        return CustomizedObject.build_obj(
            self.build_object_dict(), controller=self.controller, obj_exists=obj_exists
        )

    # ----- General Functionality ----- #

    def test_parsing_objects_succeeds(self) -> None:
        obj = SomeObject.parse_obj(self.build_object_dict())

        self.assertEqual(obj.id, "id_object")
        self.assertEqual(obj.name, "Hello")
        self.assertEqual(obj.tags, ["tag1", "tag2"])
        self.assertEqual(obj.created, Helpers.from_rfc3339_datetime("2022-03-14T08:18:38.910Z"))
        self.assertEqual(obj.translation_status, None)
        self.assertEqual(obj.nested.ref, "some_ref")
        self.assertEqual(obj._previous, {})  # pyright: reportPrivateUsage=false

    def test_building_object_succeeds(self) -> None:
        # test: test building object
        obj = SomeObject.build_obj(
            self.build_object_dict(), controller=self.controller, obj_exists=False
        )
        self.assertEqual(obj.id, "id_object")
        self.assertEqual(obj.name, "Hello")
        self.assertEqual(obj.tags, ["tag1", "tag2"])
        self.assertEqual(obj.created, Helpers.from_rfc3339_datetime("2022-03-14T08:18:38.910Z"))
        self.assertEqual(obj.translation_status, None)
        self.assertEqual(obj.nested.ref, "some_ref")
        self.assertEqual(obj._previous, {})  # pyright: reportPrivateUsage=false

        # test: building object from api response
        obj = SomeObject.build_obj(
            self.build_object_dict(), controller=self.controller, obj_exists=True
        )
        self.assertEqual(obj.id, "id_object")
        self.assertEqual(obj.name, "Hello")
        self.assertEqual(obj.tags, ["tag1", "tag2"])
        self.assertEqual(obj.created, Helpers.from_rfc3339_datetime("2022-03-14T08:18:38.910Z"))
        self.assertEqual(obj.translation_status, None)
        self.assertEqual(obj.nested.ref, "some_ref")
        self.assertDictEqual(obj._previous, obj._attrs)  # pyright: reportPrivateUsage=false

        # test: make sure objects are actually deep copied
        obj._previous["columns"][0].ref = "column_invalid"
        self.assertEqual(obj._previous["columns"][0].ref, "column_invalid")
        self.assertEqual(obj._attrs["columns"][0].ref, "column_1")

    def test_object_equivalence_fails(self) -> None:
        first = self.build_obj()

        # test: simple property differs
        second = self.build_obj()
        second.name = "This property differs"
        self.assertNotEqual(second, first)

        # test: simple nested property differs
        second = self.build_obj()
        second.nested.ref = "invalid_ref"
        self.assertNotEqual(second, first)

        # test: doubly nested property differs
        second = self.build_obj()
        second.nested.metadata.reviewed_count = 10000
        self.assertNotEqual(second, first)

        # test: simple list differs
        second = self.build_obj()
        second.tags = ["diff"]
        self.assertNotEqual(second, first)

        # test: simple nested list differs
        second = self.build_obj()
        second.columns[0].ref = "invalid_ref"
        self.assertNotEqual(second, first)

        # test: complex nested list differs
        second = self.build_obj()
        second.columns[0].metadata.reviewed_count = 10000
        self.assertNotEqual(second, first)

    def test_object_equivalence_succeeds(self) -> None:
        first = self.build_obj()

        # test: simple equivalence test
        second = self.build_obj()
        self.assertEqual(first, second)

        # test: changing properties works
        second.name = "Not the same anymore."
        self.assertNotEqual(first, second)
        second.nested.ref = "still not the same."
        self.assertNotEqual(first, second)
        second.name = "Hello"
        self.assertNotEqual(first, second)
        second.nested.ref = "some_ref"
        self.assertEqual(first, second)

    def test_modifying_forbidden_fields_fails(self) -> None:
        first = self.build_obj()

        # test: assigning simple forbidden field
        with self.assertRaisesRegex(AttributeError, "upload_status"):
            first.upload_status = "in_progress"

        # test: assigning simple nested field
        with self.assertRaisesRegex(AttributeError, "type"):
            first.nested.type = "text"

        # test: assigning doubly nested field
        with self.assertRaisesRegex(AttributeError, "some_other_field"):
            first.nested.metadata.some_other_field = 400

        # test: appending to list fails
        with self.assertRaisesRegex(ValueError, "Error appending item"):
            first.columns.append(first.columns[0])

        # test: removing from list fails
        with self.assertRaisesRegex(ValueError, "Error deleting item"):
            del first.columns[0]

        # test: replacing in list fails
        with self.assertRaisesRegex(ValueError, "Error setting item"):
            first.columns[0] = first.columns[1]

    def test_object_modified_dict_succeeds(self) -> None:
        first = self.build_obj(obj_exists=True)

        # test: nothing has changed
        modified = first.modified_dict()
        self.assertEqual(modified, NOT_SET)

        # test: simple property has changed
        first.name = "My New Name"
        modified = first.modified_dict()
        self.assertDictEqual(modified, {"name": "My New Name"})

        # test: simple list has changed
        first = self.build_obj(obj_exists=True)
        first.tags.append("new-tag")
        modified = first.modified_dict()
        self.assertDictEqual(modified, {"tags": ["tag1", "tag2", "new-tag"]})

        # test: simple date has changed
        now = datetime.now()
        first = self.build_obj(obj_exists=True)
        first.created = now
        modified = first.modified_dict()
        self.assertDictEqual(modified, {"created": now})

        # test: simple nested field has changed
        first = self.build_obj(obj_exists=True)
        first.nested.ref = "new_ref"
        modified = first.modified_dict()
        self.assertDictEqual(modified, {"nested": {"ref": "new_ref"}})

        # test: many fields have changed
        first = self.build_obj(obj_exists=True)
        now = datetime(year=2020, month=10, day=10, hour=0)
        first.name = "new name"
        first.tags = ["new-tags"]
        first.created = now
        first.nested.ref = "new_ref"
        first.nested.metadata.reviewed_count = 400
        first.columns[0].ref = "obj_ref"
        first.columns[1].metadata.reviewed_count = 200
        modified = first.modified_dict()
        self.assertDictEqual(
            modified,
            {
                "name": "new name",
                "tags": ["new-tags"],
                "created": now,
                "nested": {"ref": "new_ref", "metadata": {"reviewed_count": 400}},
                "columns": [{"ref": "obj_ref"}, {"metadata": {"reviewed_count": 200}}],
            },
        )

        # test: only partial nested list fields have changed
        first = self.build_obj(obj_exists=True)
        first.columns[0].ref = "obj_ref"
        first.columns[0].metadata.reviewed_count = 80000
        modified = first.modified_dict()
        self.assertDictEqual(
            modified,
            {"columns": [{"ref": "obj_ref", "metadata": {"reviewed_count": 80000}}]},
        )

    def test_customizing_modified_dict_succeeds(self) -> None:
        # test: nothing has changed
        first = self.build_customized(obj_exists=True)
        modified = first.modified_dict()
        self.assertEqual(modified, NOT_SET)

        # test: one entry has changed
        first = self.build_customized(obj_exists=True)
        first.columns[0].ref = "obj_ref"
        first.columns[0].metadata.reviewed_count = 80000
        modified = first.modified_dict()
        self.assertDictEqual(
            modified,
            {
                "columns": [
                    {"ref": "obj_ref", "type": "numerical", "metadata": {"reviewed_count": 80000}},
                    {"ref": "column_2", "type": "date"},
                ]
            },
        )
