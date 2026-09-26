# 專案待辦清單

## 已確認方向

- 使用 uv 管理環境，Python 3.14。
- 根目錄 `main.py` 為執行入口，五個 Server 放在 `server/`。
- 實作與驗收遵守 `AGENTS.md`。
- 內容與實作保持精簡；只保留必要驗證，移除重複或額外保險性驗證。
- 計劃已經使用者同意；每次只執行目前步驟，完成後提交結果，等使用者確認才進入下一步。
- 狀態：待執行、進行中、受阻、待確認、已完成。待確認不等於使用者已驗收。

## 執行計劃

| 步驟 | 狀態 | 待辦項目 | 確認成果 |
| --- | --- | --- | --- |
| 1 | 已完成 | 檢查現有專案、uv 設定及 Python 版本，確認目標網站網址 | 使用者已提供網址並同意下一步 |
| 2 | 已完成 | 使用 requests.Session 驗證列表第 1、7 頁，保存 HTML 樣本 | 使用者已確認兩頁成功結果 |
| 3 | 已完成 | 建立 main.py、server/ 與五個 Server；實作 Session 請求與 raise_for_status | 骨架與精簡 HTTP 層完成 |
| 4 | 已完成 | 實作列表解析、狀態篩選、ID 去重與錯誤拋出 | 列表 JSON 與測試結果 |
| 5 | 已完成 | 從列表 JSON 選取單回答、多回答詳情，保存樣本並驗證文字分離規則 | 詳情結構與清理規則 |
| 6 | 已完成 | 實作詳情解析、全部回答保留、必要欄位解析及錯誤拋出 | 詳情 JSON 與測試結果 |
| 7 | 已完成 | 從詳情 JSON 匯出 UTF-8 BOM CSV，支援動態回答欄位 | CSV 與特殊字元往返驗證 |
| 8 | 已完成 | 整合原子寫入與指定驗收案例 | 測試結果 |
| 9 | 已完成 | 正式抓取第 1～7 頁及詳情，核對唯一 ID、JSON 筆數與 CSV 列數 | 最終資料與使用說明 |

## 第 1 步檢查結果

- 已確認 uv 0.12.13、Python 3.14.3；`.python-version` 為 3.14。
- 尚未宣告或安裝 requests、beautifulsoup4，尚無 uv.lock。
- `src/main.py` 為空；目前 console script 指向不存在的 `lab_crawler:main`。
- 第 3 步改為根目錄 main.py 與 server/，整理不適用的打包設定，以 `uv run python main.py` 執行。
- 本步未安裝套件或抓取網站。使用者已確認進入第 2 步。

## 目標網址

https://0800280280.sme.gov.tw/accounting/run.php?name=forum&file=forum_list&csId=B&fId=15&page=1

## 第 2 步結果

- 已安裝 requests、beautifulsoup4，更新 pyproject.toml 並產生 uv.lock。
- 使用者提供 headers 後授權第二次嘗試：requests.Session 第 1、7 頁均 HTTP 200，取得有效列表 HTML；Cookie 僅在記憶體使用。
- 本次樣本第 1 頁 20 列、第 7 頁 13 列；排除 1 筆空白狀態，共 32 個唯一合格 ID，沒有解析異常。非永久筆數斷言。
- 列表為 `.search-list > table tbody tr`；FAQ 位於表格外的 `.search-list .faq`。
- 最新有效 HTML 與紀錄保存於 `tests/fixtures/`，已移除舊阻擋樣本與舊紀錄。使用者已確認進入第 3 步。

## 第 3 步結果

- 建立根目錄 main.py 與 server/ 五個 Server，移除空 src/main.py 及舊打包入口設定。
- HTTP 層使用單一 Session 與預設 TLS 驗證；僅用 raise_for_status 檢查狀態。
- 保留預設 2～3 秒請求間隔，由 HttpServer 建構參數調整；已移除 HttpSettings、逾時與命令列設定。
- 已依使用者修正移除重連／重試、退避、Retry-After、驗證頁偵測及相關測試檔。
- User-Agent 可由環境變數覆寫，Cookie 僅從環境變數讀入記憶體。
- 目前入口只回報骨架狀態，不抓取網站；其餘解析與輸出留待後續步驟。使用者已確認進入第 4 步。

## 第 4 步進度

- 已完成列表解析與原子 JSON 輸出；8 項必要測試通過。
- 已移除 DeduplicationServer，由 CrawlServer 遇到重複 ID 直接跳過，不合併資料。
- 第 1～7 頁抓取成功；132 個唯一 ID，無失敗或解析異常。已保存 output/forum_list.json；尚未抓取詳情。

- 執行計時已移至 main.py 入口，由 finally 印出結束時間與耗時；Server 不再保存時間欄位。

- 已移除頁碼紀錄與頁數統計；頁碼只用於抓取第 1～7 頁。

- 已移除 report、統計及 list_run.json；抓取／解析錯誤直接拋出，中斷任務，不保存部分結果或失敗清單。

## 第 5 步結果

- requests 取得單回答 580254、多回答 569200（2 答）HTML，保存於 tests/fixtures/。
- 已確認問題、回答、姓名角色日期與附加說明節點；清理規則見 tests/fixtures/README.md。
- 保留原文 Q-、條列與省略號，只分離網站附加說明；尚未實作第 6 步。

## 第 6 步結果

- 已建立 schemas/question_detail.py 與詳情解析，6 項必要測試通過。
- 依列表 JSON 抓取完成：132 筆詳情、163 個回答，ID 唯一且與列表一致。
- 輸出 output/question_details.json，保留正文、原始 HTML 與分離的 notice_text；尚未進入 CSV 步驟。

## 第 7 步結果

- 從詳情 JSON 匯出 output/qa.csv，共 132 列，ID 唯一且筆數與詳情一致。
- UTF-8 BOM、至少兩個回答欄、三回答動態欄位、空欄及逗號／引號／換行往返已確認；臨時測試檔未保留。
- 主流程已接上 CSV 匯出；本步使用既有 JSON，未重新抓取網站。

## 第 8 步結果

- 現有 3 項正文解析測試及離線整合驗收通過。
- 已確認多 tbody、狀態篩選、FAQ 排除、重複 ID 跳過、同名不同 ID、完整 JSON→CSV 流程、三回答欄位及特殊字元往返。
- 模擬 JSON／CSV 替換失敗，原結果保持完整且錯誤直接拋出。
- 未增加執行期欄位驗證或報告；臨時驗收資料已自動刪除，未重新抓取網站。
- 目前保留單／多回答 HTML；第 1、7 頁原始 HTML 已不在專案，第 9 步正式抓取時補存最新樣本。

## 第 9 步結果

- 完整流程正式執行成功，入口回傳 0；耗時 358.70 秒（含請求間隔與輸出）。
- 列表、詳情及 CSV 均為 132 筆，163 個回答，ID 唯一且一致，CSV 正文與詳情一致。
- 已更新 output/forum_list.json、output/question_details.json、output/qa.csv，並補存第 1、7 頁最新 HTML。
- 執行方式：`uv run python main.py`。
