# 專案代理工作規範

本文件適用於整個專案。實作、修改、執行與驗收爬蟲時，均須遵守以下規範。

內容、實作與回報保持精簡。只保留確認需求與正確性所必需的驗證；不新增或保留重複、額外保險性驗證。以下明列的必要驗收仍須完成。

驗證產物只保留最新執行結果與必要 HTML 樣本，移除已被取代的舊結果與臨時驗證檔。

本專案以 Python `requests.Session` 進行 HTTP 存取，使用 BeautifulSoup 解析 HTML。瀏覽器僅用於人工結構驗證；不得將瀏覽器成功載入宣稱為 requests 抓取成功。

## 1. 抓取範圍與流程

- 固定抓取 `csId=B`、`fId=15`、`page=1..7` 的列表表格。
- 排除常見問題區（FAQ）、導覽及頁尾連結。
- 先完成列表 JSON，再根據該 JSON 抓取詳情，最後由詳情 JSON 產生 CSV。

## 2. 列表篩選

- 遍歷所有 `tbody` 的資料列。
- 回覆狀態欄位文字須包含「已回覆」才收錄；空白或其他狀態一律跳過。
- 依固定結構直接讀取狀態欄位，不額外檢查節點是否存在。

## 3. ID 與去重

- ID 使用詳情 URL 的 `p` 參數，以字串保存。
- 列表及詳情 JSON 均以 ID 去重。遇到相同 ID 直接跳過，只保留第一筆，不合併資料。
- 不同 ID 即使標題相同也不得直接合併。
- 直接讀取 URL 的 p 參數，不驗證 ID 格式，也不自行編號替代。

## 4. JSON 欄位

- 列表資料至少包含 `id`、`title`、`url`、`reply_status`、`published_at`。
- 詳情資料沿用列表欄位，另包含 `question`、`question_raw_html`、`asker_name`、`industry`、`region`、`asked_at`、`view_count`、`answers`、`fetched_at`。
- `answers` 為陣列，每項包含 `order`、`accountant_name`、`accountant_role`、`answered_at`、`text`、`raw_html`、`notice_text`。
- `published_at` 為必填字串，直接讀取網站內容。
- Answer 與 QuestionDetail 所有欄位皆為必填型別；不新增手動欄位存在、空白或格式驗證。

## 5. 文字清理

- 保留繁體中文、標點、段落、條列與換行；HTML entity 正常解碼。
- 只移除網站附加的開頭 `Q：`／`A：`。
- 共用說明與宣傳文字須依已驗證規則分離，保留原始 HTML 供追溯。
- 不得摘要、改寫或自行補齊看似不完整的答案。

## 6. 回答與 CSV

- 收錄每個會計師回答區塊，依頁面順序排列；同一會計師的多次回答也須保留。
- CSV 欄名固定以 `ID,Question,Answer1,Answer2` 開始，再依整批資料最大回答數增加 `Answer3` 等欄位；至少保留 `Answer1`、`Answer2`。
- `Question` 對應問題正文；`AnswerN` 對應清理後回答正文。
- 缺少的回答欄填空字串。
- 使用標準 CSV 寫入器處理逗號、雙引號及換行，輸出 UTF-8 BOM。
- JSON 使用 UTF-8 並直接保留中文字元。

## 7. 成功與失敗判定

- HTTP 層僅使用 requests 的 `response.raise_for_status()` 檢查狀態，不額外偵測驗證頁。
- HTTP、連線及逾時錯誤直接向上拋出，不自動重連、重試、退避或處理 `Retry-After`。
- 列表與詳情依固定結構直接取值，保留 Pydantic 型別建模；不額外檢查欄位、正文或回答是否存在。

## 8. HTTP 存取與續跑

- 使用單一 requests.Session，預設請求間隔 2～3 秒，由 HttpServer 建構參數調整；不添加逾時或並行設定。
- 使用正常 TLS 驗證。
- 任務錯誤直接拋出並中斷，不保存失敗清單、部分進度或自動續跑。
- 輸出採暫存檔完成後替換，避免中斷造成 JSON 損毀。

## 9. 執行輸出

- 不建立 report、統計或執行紀錄 JSON；僅輸出資料檔。
- 抓取與解析錯誤直接 raise，讓任務中斷並顯示錯誤。
- main.py 入口印出開始／結束時間及總耗時，Server 不負責計時。

## 10. 物件責任與五行原則

使用以下物件區分責任：

| 物件 | 責任 |
| --- | --- |
| `HttpServer` | HTTP 存取 |
| `ForumListServer` | 列表解析 |
| `QuestionDetailServer` | 詳情解析 |
| `ExportServer` | 輸出 |
| `CrawlServer` | 流程協調及重複 ID 跳過 |

- `Server` 在此代表邏輯物件，不代表必須啟動網路服務。
- 方法名稱須描述用途，例如 `parse_question_detail`、`export_qa_csv`。
- 所有函式與方法都須明確標註參數及回傳值型別，以提升可讀性與可維護性；`self`、`cls` 不需額外標註。
- 無回傳值使用 `-> None`；空值使用 `None`，可空型別使用 `T | None`（不使用 `Optional`）；容器須標註元素型別，例如 `list[str]`。避免以 `Any` 取代已知型別。
- 採用五行原則：每個方法主體最多五個非空白、非註解實體行。
- 不可用分號或過長單行規避，應拆成有意義的單一職責方法。

## 11. 驗收

- 保存第 1、7 頁與單回答、多回答詳情的 HTML 測試樣本。
- 驗證多 `tbody`、空白狀態排除、FAQ 排除、ID 去重、宣傳文字分離。
- 驗證三個以上回答的動態欄位，以及 CSV 換行／引號往返。
- 最終 CSV 資料列數須等於成功詳情 JSON 筆數，ID 必須唯一。
- 即時網站筆數可能變動，不以本次觀察的 20／13 筆作永久斷言。

## 寫法與格式

- 資料模型使用 Pydantic BaseModel，不使用 TypedDict 或 cast。
- Pydantic 模型統一放在根目錄 schemas/，依用途分檔（例如 schemas/forum_list.py）；Server 只匯入模型，不在其中定義。
- 語意相同時優先正向條件；需要區分 None 與空字串、零、空容器時保留明確判斷。
- 使用 `uv run ruff format .` 統一格式，設定以 pyproject.toml 為準。
