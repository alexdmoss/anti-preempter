from anti_preempter import google_client
import google.oauth2


def test_build_creds_object(monkeypatch):
    with open('./tests/mocks/mock-creds.json', 'r') as f:
        fake_credentials = f.read()
    monkeypatch.setenv('PROJECT_READER_CREDS', fake_credentials)
    obj = google_client.build_creds_object('PROJECT_READER_CREDS')
    assert isinstance(obj, google.oauth2.service_account.Credentials)
