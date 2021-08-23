from gcp.utils import get_resource_object_type, get_unique_identifier_from_name


def test_get_get_unique_identifier_from_name():
    expected: str = 'folders/188906894377'
    name: str = '//cloudresourcemanager.googleapis.com/folders/188906894377'
    actual: str = get_unique_identifier_from_name(name)
    assert actual == expected


def test_get_resource_object_type():
    expected: str = 'Folder'
    asset_type: str = 'cloudresourcemanager.googleapis.com/Folder'
    actual: str = get_resource_object_type(asset_type)
    assert actual == expected
