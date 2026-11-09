import shutil
import tempfile
from types import TracebackType


class TempDir:
    def __init__(self) -> None:
        self.temp_dir: str | None = None

    def __enter__(self) -> str:
        self.temp_dir = tempfile.mkdtemp(prefix="scanpdf_")
        return self.temp_dir

    # noinspection PyUnusedLocal
    def __exit__(
        self,
        type_value: type[BaseException],
        value: BaseException,
        traceback: TracebackType,
    ) -> None:
        if self.temp_dir is not None:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
