import unittest
from unittest.mock import patch
from wiz.cli import build_parser, handle_cli_args

class TestWizCLI(unittest.TestCase):

    def setUp(self):
        self.parser = build_parser()

    @patch("wiz.cli.init_project_config")
    def test_init_command(self, mock_init):
        args = self.parser.parse_args(["init", "--path", "."])
        handle_cli_args(args)
        mock_init.assert_called_once_with(".")

    @patch("wiz.cli.load_config", return_value={"default_engine": "uv"})
    @patch("wiz.cli.run_cmd")
    def test_venv_command(self, mock_run_cmd, mock_load_config):
        args = self.parser.parse_args(["venv", "--path", "test_env", "--python", "3.11"])
        handle_cli_args(args)
        mock_run_cmd.assert_called_once_with(
            ["uv", "venv", "test_env", "--python", "3.11"],
            status_msg="Configuring virtual environment"
        )

    @patch("wiz.cli.load_config", return_value={"default_engine": "uv"})
    @patch("wiz.cli.run_pip_with_progress")
    @patch("wiz.cli.validate_package", return_value=True)
    def test_install_command(self, mock_validate, mock_run_pip, mock_load_config):
        args = self.parser.parse_args(["install", "requests", "rich", "--engine", "uv"])
        handle_cli_args(args)
        mock_run_pip.assert_called_once_with(
            ["uv", "pip", "install", "requests", "rich"],
            target_action="install",
            engine_name="uv"
        )

    @patch("wiz.cli.load_config", return_value={"default_engine": "uv"})
    @patch("wiz.cli.run_cmd")
    def test_run_command(self, mock_run_cmd, mock_load_config):
        args = self.parser.parse_args(["run", "script.py", "--", "--debug", "--verbose"])
        handle_cli_args(args)
        mock_run_cmd.assert_called_once_with(
            ["uv", "run", "script.py", "--debug", "--verbose"],
            use_status=False,
            is_script=True
        )

    @patch("wiz.cli.load_config", return_value={"default_engine": "uv"})
    @patch("wiz.cli.run_cmd")
    def test_list_command(self, mock_run_cmd, mock_load_config):
        args = self.parser.parse_args(["list"])
        handle_cli_args(args)
        mock_run_cmd.assert_called_once_with(
            ["uv", "python", "list"],
            status_msg="Gathering engine runtimes"
        )

if __name__ == "__main__":
    unittest.main()
