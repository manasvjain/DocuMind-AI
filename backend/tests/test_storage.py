import sys; sys.path.insert(0,'backend')
import pytest
from app.services.storage import Storage
def test_storage_rejects_path_traversal():
    storage=Storage()
    with pytest.raises(ValueError): storage.path('../outside.txt')
    with pytest.raises(ValueError): storage.path('/absolute/path.txt')
