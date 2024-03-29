# pylint: disable=missing-module-docstring,unused-argument
from os import path
from unittest import TestCase
from unittest.mock import Mock, patch

from jenkins.github_helpers import GitHubHelper
from jenkins.pull_request_creator import PullRequestCreator


class UpgradePythonRequirementsPullRequestTestCase(TestCase):
    """
    Test Case class for PR creator.
    """

    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.close_existing_pull_requests',
           return_value=[])
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_github_instance', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.repo_from_remote', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_updated_files_list', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_current_commit', return_value='1234567')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.branch_exists', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.update_list_of_files', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_pull_request')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_branch', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator._get_user',
           return_value=Mock(name="fake name", login="fake login"))
    @patch('jenkins.github_helpers.GitHubHelper.delete_branch', return_value=None)
    def test_no_changes(self, delete_branch_mock, get_user_mock, create_branch_mock, create_pr_mock,
                        update_files_mock, branch_exists_mock, current_commit_mock,
                        modified_list_mock, repo_mock, authenticate_mock,
                        close_existing_prs_mock):
        """
        Ensure a merge with no changes to db files will not result in any updates.
        """
        pull_request_creator = PullRequestCreator('--repo_root=../../edx-platform', 'upgrade-branch', [],
                                                  [], 'Upgrade python requirements', 'Update python requirements',
                                                  'make upgrade PR')
        pull_request_creator.create(True)

        assert authenticate_mock.called
        assert repo_mock.called
        assert modified_list_mock.called
        assert not branch_exists_mock.called
        assert not create_branch_mock.called
        assert not update_files_mock.called
        assert not create_pr_mock.called

    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.close_existing_pull_requests',
           return_value=[])
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_github_instance',
           return_value=Mock())
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.repo_from_remote', return_value=Mock())
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_updated_files_list',
           return_value=["requirements/edx/base.txt", "requirements/edx/coverage.txt"])
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_current_commit', return_value='1234567')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.branch_exists', return_value=False)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.update_list_of_files', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_pull_request')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_branch', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator._get_user',
           return_value=Mock(name="fake name", login="fake login"))
    @patch('jenkins.github_helpers.GitHubHelper.delete_branch', return_value=None)
    def test_changes(self, delete_branch_mock, get_user_mock, create_branch_mock, create_pr_mock,
                     update_files_mock, branch_exists_mock, current_commit_mock,
                     modified_list_mock, repo_mock, authenticate_mock,
                     close_existing_prs_mock):
        """
        Ensure a merge with no changes to db files will not result in any updates.
        """
        pull_request_creator = PullRequestCreator('--repo_root=../../edx-platform', 'upgrade-branch', [],
                                                  [], 'Upgrade python requirements', 'Update python requirements',
                                                  'make upgrade PR')
        pull_request_creator.create(True)

        assert branch_exists_mock.called
        assert create_branch_mock.called
        self.assertEqual(create_branch_mock.call_count, 1)
        assert update_files_mock.called
        self.assertEqual(update_files_mock.call_count, 1)
        assert create_pr_mock.called

        create_pr_mock.title = "Python Requirements Update"
        create_pr_mock.diff_url = "/"
        create_pr_mock.repository.name = 'repo-health-data'

        basepath = path.dirname(__file__)

        filepath = path.abspath(path.join(basepath, "test_data", "diff.txt"))
        with open(filepath, "r") as f:
            content = f.read().encode('utf-8')
            with patch('requests.get') as mock_request:
                mock_request.return_value.content = content
                mock_request.return_value.status_code = 200
                GitHubHelper().verify_upgrade_packages(create_pr_mock)
            assert create_pr_mock.create_issue_comment.called
            assert not delete_branch_mock.called

    @patch('jenkins.pull_request_creator.PullRequestCreator._get_user',
           return_value=Mock(name="fake name", login="fake login"))
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_github_instance',
           return_value=Mock())
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.repo_from_remote', return_value=Mock())
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_updated_files_list',
           return_value=["requirements/edx/base.txt", "requirements/edx/coverage.txt"])
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_current_commit', return_value='1234567')
    # all above this unused params, no need to interact with those mocks
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.branch_exists', return_value=False)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.update_list_of_files', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_pull_request')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_branch', return_value=None)
    @patch('builtins.print')
    def test_outputs_url_on_success(self, print_mock, create_branch_mock, create_pr_mock,
                                    update_files_mock, branch_exists_mock, *args):
        """
        Ensure that a successful run outputs the URL consumable by github actions
        """
        pull_request_creator = PullRequestCreator('--repo_root=../../edx-platform', 'upgrade-branch', [],
                                                  [], 'Upgrade python requirements', 'Update python requirements',
                                                  'make upgrade PR', output_pr_url_for_github_action=True)
        pull_request_creator.create(False)

        assert branch_exists_mock.called
        assert create_branch_mock.called
        self.assertEqual(create_branch_mock.call_count, 1)
        assert update_files_mock.called
        self.assertEqual(update_files_mock.call_count, 1)
        assert create_pr_mock.called
        assert print_mock.called_once
        found_matching_call = False
        for call in print_mock.call_args_list:
            if 'set-output' in call.args[0]:
                found_matching_call = True
        assert found_matching_call

    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.close_existing_pull_requests',
           return_value=[])
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_github_instance', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.repo_from_remote', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_updated_files_list',
           return_value=["requirements/edx/base.txt", "requirements/edx/coverage.txt"])
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_current_commit', return_value='1234567')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.branch_exists', return_value=True)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.update_list_of_files', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_pull_request')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_branch', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator._get_user',
           return_value=Mock(name="fake name", login="fake login"))
    @patch('jenkins.github_helpers.GitHubHelper.delete_branch', return_value=None)
    def test_branch_exists(self, delete_branch_mock, get_user_mock, create_branch_mock, create_pr_mock,
                           update_files_mock, branch_exists_mock, current_commit_mock,
                           modified_list_mock, repo_mock, authenticate_mock,
                           close_existing_prs_mock):
        """
        Ensure if a branch exists and delete_old_pull_requests is set to False, then there are no updates.
        """
        pull_request_creator = PullRequestCreator('--repo_root=../../edx-platform', 'upgrade-branch', [],
                                                  [], 'Upgrade python requirements', 'Update python requirements',
                                                  'make upgrade PR')
        pull_request_creator.create(False)

        assert branch_exists_mock.called
        assert not create_branch_mock.called
        assert not create_pr_mock.called
        assert not delete_branch_mock.called

    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.close_existing_pull_requests',
           return_value=[])
    @patch('jenkins.pull_request_creator.PullRequestCreator._get_user',
           return_value=Mock(name="fake name", login="fake login"))
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_github_instance',
           return_value=Mock())
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.repo_from_remote', return_value=Mock())
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_updated_files_list',
           return_value=["requirements/edx/base.txt", "requirements/edx/coverage.txt"])
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_current_commit', return_value='1234567')
    # all above this unused params, no need to interact with those mocks
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.branch_exists', return_value=True)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.update_list_of_files', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_pull_request')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_branch', return_value=None)
    @patch('jenkins.github_helpers.GitHubHelper.delete_branch', return_value=None)
    @patch('builtins.print')
    def test_branch_deletion(self, create_branch_mock, create_pr_mock,
                             update_files_mock, branch_exists_mock, delete_branch_mock, *args):
        """
        Ensure if a branch exists and delete_old_pull_requests is set, then branch is deleted
        before creating new PR.
        """
        pull_request_creator = PullRequestCreator('--repo_root=../../edx-platform', 'upgrade-branch', [],
                                                  [], 'Upgrade python requirements', 'Update python requirements',
                                                  'make upgrade PR', output_pr_url_for_github_action=True)
        pull_request_creator.create(True)

        assert branch_exists_mock.called
        assert delete_branch_mock.called
        assert create_branch_mock.called
        assert update_files_mock.called
        assert create_pr_mock.called

    def test_compare_upgrade_difference_with_major_changes(self):
        basepath = path.dirname(__file__)
        filepath = path.abspath(path.join(basepath, "test_data", "diff.txt"))
        with open(filepath, "r") as f:
            valid, suspicious = GitHubHelper().compare_pr_differnce(f.read())
            assert sorted(
                ['certifi', 'chardet', 'filelock', 'pip-tools', 'platformdirs', 'pylint', 'virtualenv']
            ) == [g['name'] for g in valid]

            assert sorted(
                ['cachetools', 'six', 'tox', 'pyproject-api', 'colorama', 'py', 'chardet', 'pyparsing', 'packaging']
            ) == [g['name'] for g in suspicious]

    def test_compare_upgrade_difference_with_minor_changes(self):
        basepath = path.dirname(__file__)
        filepath = path.abspath(path.join(basepath, "test_data", "minor_diff.txt"))
        with open(filepath, "r") as f:
            valid, suspicious = GitHubHelper().compare_pr_differnce(f.read())
            assert sorted(
                ['packaging']
            ) == [g['name'] for g in valid]

            assert sorted(
                []
            ) == [g['name'] for g in suspicious]

    def test_check_automerge_variable_value(self):
        with patch('requests.get') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = {
                'name': 'ENABLE_AUTOMERGE_FOR_DEPENDENCIES_PRS', 'value': 'True',
                'created_at': '2023-03-17T12:58:50Z', 'updated_at': '2023-03-17T13:01:12Z'
            }
            self.assertTrue(
                GitHubHelper().check_automerge_variable_value(
                    'https://foo/bar/testrepo/pulls/1'
                )
            )

            # in case of false value of variable.
            mock_request.return_value.json.return_value = {
                'name': 'ENABLE_AUTOMERGE_FOR_DEPENDENCIES_PRS', 'value': 'False',
                'created_at': '2023-03-17T12:58:50Z', 'updated_at': '2023-03-17T13:01:12Z'
            }
            self.assertFalse(
                GitHubHelper().check_automerge_variable_value(
                    'https://foo/bar/testrepo/pulls/1'
                )
            )
            # in case of no variable exists.
            mock_request.return_value.status_code = 404
            mock_request.return_value.json.return_value = {
                'name': 'ENABLE_AUTOMERGE_FOR_DEPENDENCIES_PRS', 'value': 'False',
                'created_at': '2023-03-17T12:58:50Z', 'updated_at': '2023-03-17T13:01:12Z'
            }
            self.assertFalse(
                GitHubHelper().check_automerge_variable_value(
                    'https://foo/bar/testrepo/pulls/1'
                )
            )

    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.close_existing_pull_requests',
           return_value=[])
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_github_instance',
           return_value=Mock())
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.repo_from_remote', return_value=Mock())
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_updated_files_list',
           return_value=["requirements/edx/base.txt", "requirements/edx/coverage.txt"])
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.get_current_commit', return_value='1234567')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.branch_exists', return_value=False)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.update_list_of_files', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_pull_request')
    @patch('jenkins.pull_request_creator.PullRequestCreator.github_helper.create_branch', return_value=None)
    @patch('jenkins.pull_request_creator.PullRequestCreator._get_user',
           return_value=Mock(name="fake name", login="fake login"))
    @patch('jenkins.github_helpers.GitHubHelper.delete_branch', return_value=None)
    def test_changes_with_minor_versions_and_variable(
        self, delete_branch_mock, get_user_mock, create_branch_mock, create_pr_mock,
        update_files_mock, branch_exists_mock, current_commit_mock,
        modified_list_mock, repo_mock, authenticate_mock,
        close_existing_prs_mock
    ):
        """
        Ensure a merge with no changes to db files will not result in any updates.
        """
        pull_request_creator = PullRequestCreator('--repo_root=../../edx-platform', 'upgrade-branch', [],
                                                  [], 'Upgrade python requirements', 'Update python requirements',
                                                  'make upgrade PR')
        pull_request_creator.create(True)

        assert branch_exists_mock.called
        assert create_branch_mock.called
        self.assertEqual(create_branch_mock.call_count, 1)
        assert update_files_mock.called
        self.assertEqual(update_files_mock.call_count, 1)
        assert create_pr_mock.called

        create_pr_mock.title = "Python Requirements Update"
        create_pr_mock.diff_url = "/"
        create_pr_mock.repository.name = 'repo-health-data'

        basepath = path.dirname(__file__)

        filepath = path.abspath(path.join(basepath, "test_data", "minor_diff.txt"))
        with open(filepath, "r") as f:
            content = f.read().encode('utf-8')
            with patch('requests.get') as mock_request:
                mock_request.return_value.content = content
                mock_request.return_value.status_code = 200

                # in case of `check_automerge_variable_value` false value label will not added.
                with patch(
                        'jenkins.github_helpers.GitHubHelper.check_automerge_variable_value'
                ) as check_automerge_variable_value:
                    check_automerge_variable_value.return_value = False
                    GitHubHelper().verify_upgrade_packages(create_pr_mock)
                    assert not create_pr_mock.set_labels.called
