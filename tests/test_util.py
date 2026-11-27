import os
import shutil
from unittest.mock import patch

from scan_pdf import TempDir

from . import touch


class TestTempdir:
    def test_tempdir(self):
        temp_dir_path = None

        with TempDir() as temp_dir:
            temp_dir_path = temp_dir

            assert os.path.isdir(temp_dir)
            assert os.path.basename(temp_dir).startswith("scanpdf_")
            assert os.listdir(temp_dir) == []

            touch(os.path.join(temp_dir, "foo.txt"))
            touch(os.path.join(temp_dir, "bar.txt"))

            file_names = os.listdir(temp_dir)
            for file_name in ["bar.txt", "foo.txt"]:
                assert file_name in file_names

        assert not os.path.exists(temp_dir_path)

    def test_tempdir_already_removed(self):
        with TempDir() as temp_dir:
            shutil.rmtree(temp_dir)

        assert not os.path.exists(temp_dir)

    def test_exit_without_enter(self):
        with patch("scan_pdf.util.shutil.rmtree") as rmtree:
            TempDir().__exit__(None, None, None)

        rmtree.assert_not_called()
