from dispatch.plugins.bases import StoragePlugin


class TestStoragePlugin(StoragePlugin):
    title = "Dispatch Test Plugin - Storage"
    slug = "test-storage"

    def get(self, **kwargs):
        return

    def create(self, items, **kwargs):
        return

    def update(self, items, **kwargs):
        return

    def delete(self, items, **kwargs):
        return

    def list(self, **kwargs):
        return

    def add_participant(self, items, **kwargs):
        return

    def remove_participant(self, items, **kwargs):
        return

    def add_file(self, **kwargs):
        return

    def delete_file(self, **kwargs):
        return

    def move_file(self, **kwargs):
        return

    def list_files(self, **kwargs):
        return
