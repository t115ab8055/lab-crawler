import csv
import json
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel

from schemas.question_detail import QuestionDetail


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

    def export_qa_csv(self, records: Sequence[QuestionDetail], path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        self._write_qa_csv(records, temporary)
        temporary.replace(path)

    def _write_qa_csv(self, records: Sequence[QuestionDetail], path: Path) -> None:
        count = max(2, max((len(record.answers) for record in records), default=0))
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["ID", "Question"] + [f"Answer{i}" for i in range(1, count + 1)])
            writer.writerows(self._qa_row(record, count) for record in records)

    def _qa_row(self, record: QuestionDetail, count: int) -> list[str]:
        answers = [answer.text for answer in record.answers]
        return [record.id, record.question] + answers + [""] * (count - len(answers))
