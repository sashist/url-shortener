from db import Link
from repositories.base import BaseRepository


class LinkRepository(BaseRepository[Link]):
    model = Link

    def create_link(self, link_data):
        # Logic to create a new link in the database
        pass

    def get_link(self, link_id):
        # Logic to retrieve a link by its ID from the database
        pass

    def update_link(self, link_id, link_data):
        # Logic to update an existing link in the database
        pass

    def delete_link(self, link_id):
        # Logic to delete a link from the database
        pass

    def list_links(self):
        # Logic to list all links from the database
        pass