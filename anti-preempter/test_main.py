import main
import pytest
# import json


@pytest.fixture(autouse=True)
def set_stub_reader_creds(mocker):
    mocker.patch('main.create_k8s_client')


# def test_list_preemptible_nodes_by_creation_time(mocker):
#     with open("test_response.json", 'r') as f:
#         test_response = json.load(f)
#     node_list = mocker.patch('main.list_nodes')
#     node_list.return_value = [test_response]
#     nodes = main.list_preemptible_nodes_by_creation_time()
#     assert 'gke' in nodes

# def test_find_nodes_to_restart():

# def test_delete_node():

# def test_create_k8s_client():


# def test_main():

def test_init(mocker):
    # run wrapper validity: https://medium.com/opsops/how-to-test-if-name-main-1928367290cb
    mocker.patch.object(main, "main", return_value=42)
    mocker.patch.object(main, "__name__", "__main__")
    mocker.patch.object(main.sys, 'exit')
    main.init()
    assert main.sys.exit.call_args[0][0] == 42
