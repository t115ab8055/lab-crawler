# lab-crawler

使用 uv、Python 3.14；入口為 `main.py`，五個邏輯物件位於 `server/`。

```sh
uv sync
uv run python main.py
```

列表流程：抓取 `csId=B`、`fId=15`、第 1～7 頁列表，僅保留已回覆資料；遇到重複 `p` ID 直接跳過，不合併資料。

列表寫入 `output/forum_list.json` 後，讀取該 JSON 抓取詳情，完成後寫入 `output/question_details.json`，再讀取詳情 JSON 匯出 `output/qa.csv`。每次成功執行覆寫。抓取或解析錯誤直接拋出並中斷，不輸出統計或失敗清單。

main.py 入口印出開始／結束時間與總耗時。CSV 使用 UTF-8 BOM，欄位為 `ID,Question,Answer1,Answer2`，依最大回答數擴充，缺少的回答留空。

HTTP 使用單一 Session，預設請求間隔 2～3 秒，由 `HttpServer(interval_min=2.0, interval_max=3.0)` 調整。僅使用 `raise_for_status()` 檢查 HTTP 狀態；無逾時設定、重連或重試，保留預設 TLS 驗證。

資料模型使用 Pydantic，依用途放在 `schemas/`。格式化：`uv run ruff format .`（Python 3.14、每行 100 字元、雙引號、空格縮排）。

詳情保留問題、全部回答與原始 HTML；附加說明另存 `notice_text`，不改寫正文。直接依固定結構讀取欄位，不額外驗證欄位存在或內容。
