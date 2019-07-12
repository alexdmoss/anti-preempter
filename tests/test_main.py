import pytest
import main
# import os
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    with open('./tests/mocks/mock-creds.json', 'r') as f:
        fake_credentials = f.read()
    monkeypatch.setenv('GOOGLE_CREDS', fake_credentials)
    monkeypatch.setenv('GCP_PROJECT_ID', "fake-gcp-project")
    monkeypatch.setenv('INSTANCE_INTERVAL', '600')

# def test_create_costs_report(mocker, monkeypatch, tmp_path):

#     test_file = "platform-costs.pytest.md"

#     monkeypatch.setenv('OUTPUT_DIR', str(tmp_path))
#     monkeypatch.setenv('REPORT_FILE', test_file)

#     test_data = [
#         ['project-1-flex', 201905, 1.64],
#         ['project-1-flex', 201906, 0.37],
#         ['project-1-prod', 201905, 1.65],
#         ['project-1-prod', 201906, 0.37],
#         ['project-2-test', 201805, 2.51],
#         ['project-2-test', 201806, 4.96],
#         ['project-2-prod', 201807, 4.98],
#         ['project-2-prod', 201808, 4.77]
#     ]

#     df = pd.DataFrame(test_data)
#     df.columns = (['project', 'month', 'spend'])

#     stub_project_list = mocker.patch('main.list_projects')
#     stub_project_list.return_value = ['project-1-flex', 'project-1-prod']

#     main.create_costs_report(df)

#     f = open(tmp_path / test_file, "r")
#     result = f.read()
#     f.close()

#     assert "title: " in result
#     assert "Last Generated" in result
#     assert "weight: " in result

#     # these tests may be brittle if wording changes a lot - consider removing
#     assert "JLDP v1 Costs" in result
#     assert "version 1 platform runs" in result
#     assert "JLDP v2 Tenant Costs" in result
#     assert "GCP services outside" in result
#     assert "JLDP v2 Platform Costs" in result
#     assert "includes costs" in result
#     assert "Other JL Commerce Projects" in result
#     assert "not treated as JLDP projects" in result


# def test_create_cost_charts(mocker, monkeypatch, tmp_path):

#     monkeypatch.setenv('OUTPUT_DIR', str(tmp_path))

#     stub_project_list = mocker.patch('main.list_projects')
#     stub_project_list.return_value = ['project-1-flex', 'project-1-prod']

#     test_data = "./tests/mocks/raw_df.csv"
#     df = pd.read_csv(test_data, index_col=0)

#     main.create_cost_charts(df)

#     # Note that with this test we are not checking the content of the png is valid!
#     num_png_files = len([f for f in os.listdir(tmp_path)
#                          if f.endswith('.png') and os.path.isfile(os.path.join(tmp_path, f))])
#     # could turn out to be brittle - 4 sections in the SECTIONS static in main.py
#     assert num_png_files == 4


# def test_main_no_args(mocker):
#     mocker.patch('main.list_projects')
#     mocker.patch('main.query_monthly_spend')
#     mocker.patch('main.create_cost_charts')
#     mocker.patch('main.create_costs_report')

#     runner = CliRunner()
#     result = runner.invoke(main.main)

#     assert result.output == 'No project specified - reporting on all projects\n'


# def test_main_with_project(mocker):
#     mocker.patch('main.list_projects')
#     mocker.patch('main.query_monthly_spend')
#     mocker.patch('main.create_cost_charts')
#     mocker.patch('main.create_costs_report')

#     runner = CliRunner()
#     result = runner.invoke(main.main, ['--project', 'jl-platform-k8s-verify'])

#     assert result.output == 'Building report for jl-platform-k8s-verify project\n'


def test_init(mocker):
    # run wrapper validity: https://medium.com/opsops/how-to-test-if-name-main-1928367290cb
    mocker.patch.object(main, "main", return_value=42)
    mocker.patch.object(main, "__name__", "__main__")
    mocker.patch.object(main.sys, 'exit')
    main.init()
    assert main.sys.exit.call_args[0][0] == 42
