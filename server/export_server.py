import json
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel


class ExportServer:
    """以暫存檔替換方式輸出 UTF-8 JSON。"""

    def export_json(self, records: Sequence[BaseModel], path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(self._serialize(records), encoding="utf-8")
        temporary.replace(path)

    def _serialize(self, records: Sequence[BaseModel]) -> str:
        data = [record.model_dump(mode="json") for record in records]
        return json.dumps(data, ensure_ascii=False, indent=2)

    def export_qa_csv(self, records: Sequence[BaseModel], path: str | Path) -> None:
        raise NotImplementedError("CSV 輸出待第 7 步實作")
