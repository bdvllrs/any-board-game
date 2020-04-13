import pytest

import game_engine.server as server


@pytest.fixture
def client():
    server.app.config['TESTING'] = True

    with server.app.test_client() as client:
        yield client


def test_create_and_join_round(client):
    game_name = "bataille"
    usernames = ["test1", "test2", "test3"]
    response = client.post(f"/round/create/{game_name}",
                           data=dict(username=usernames[0]))
    response_data = response.get_json()
    assert response_data['createdBy'] == usernames[0]
    assert response_data['id'] in server.games
    # TODO: extra checks
