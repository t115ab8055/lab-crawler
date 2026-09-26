import json
from pathlib import Path


class ExportServer:
    """以暫存檔替換方式輸出 UTF-8 JSON。"""

    def export_json(self, records, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)

    def export_qa_csv(self, records, path):
        raise NotImplementedError("CSV 輸出待第 7 步實作")
