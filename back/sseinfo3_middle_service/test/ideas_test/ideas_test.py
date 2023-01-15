import time
from werkzeug.test import Client
from pytest import mark

from entities.ideas_entity import IdeaEntity


@mark.usefixtures("app", "client", "app_ctx")
class TestIdea:

    def test_for_creation(self, client):
        response = client.post("/api/v1/ideas", data=dict(title="title1", text="text1"))
        assert response.status_code == 200
        content = response.json["data"]
        assert content["title"] == "title1"
        assert content["text"] == "text1"
        return response.json["data"]["id"]

    def test_for_update(self, client, app_ctx):
        self.reserver_record()
        time.sleep(1)
        response = client.put("/api/v1/ideas/1", data=dict(title="new_title", text="new_text"))
        assert response.status_code == 200
        content = response.json["data"]
        assert content["id"] == 1
        assert content["last_update_time"] > content["create_time"]
        assert content["title"] == "new_title"
        assert content["text"] == "new_text"

    def test_for_delete(self, client, _id=1):
        response = client.delete(f"/api/v1/ideas/{_id}", )
        assert response.status_code == 200

        # read for success
        response = client.get(f"/api/v1/ideas/{_id}")
        response.status_code == 200
        response.json["data"] == ""

    def test_for_read_detail(self, client, app_ctx):
        self.reserver_record()
        response = client.get("/api/v1/ideas/1")
        assert response.status_code == 200
        content = response.json
        assert content["data"]["id"] == 1

    def test_for_read_list(self, client, app_ctx):
        _id = self.test_for_creation(client)
        response = client.get("/api/v1/ideas", query_string=dict(title="title1", page=1, size=10))
        assert response.status_code == 200
        assert isinstance(response.json["data"]["records"], list)
        assert response.json["data"]["count"] == 1
        self.test_for_delete(client, _id)
        response = client.get("/api/v1/ideas", query_string=dict(title="title1", page=1, size=10))
        assert response.status_code == 200
        assert isinstance(response.json["data"]["records"], list)
        assert response.json["data"]["count"] == 0

    def reserver_record(self):
        instance = IdeaEntity.query.get(1)
        instance.active = True
        IdeaEntity.query.session.commit()
