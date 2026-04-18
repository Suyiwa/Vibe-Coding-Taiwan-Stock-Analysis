# Vibe-Coding-Taiwan-Stock-Analysis
AI-assisted stock technical analysis system using Gemini, ChatGPT, and Claude. Features automated K-line plotting and indicator analysis (MA, MACD, RSI).

# AI 輔助股票技術指標分析系統 
### AI-Powered Stock Analysis System (Multi-LLM Collaboration)

這是一個基於 Python 開發的專業股票分析工具，結合了技術面指標與基本面數據。本專案最大的特色在於開發過程全面導入生成式 AI（ChatGPT, Gemini, Claude）進行跨模型協作，構建出具備多維度評分系統的投資輔助工具。

---

## AI 工具協作紀錄 (AI Collaboration)
本專案核心開發流程如下：
* **ChatGPT (GPT-4)**：負責初期專案架構規劃與非程式類的股票專業分類邏輯。
* **Google Gemini**：負責編寫核心計算邏輯與 Python 初版程式碼，並於 Google Colab 進行即時驗證。
* **Claude 3.5**：負責程式碼重構、Debug 以及將 Colab 腳本轉化為`.py` 模組，優化系統框架。

---

## 核心功能 (Core Features)
* **多市場支援**：支援台股 (.TW)、美股、港股 (.HK) 等Yahoo Finance 可搜尋之股票。
* **技術指標計算**：包含 MA (5/20/60)、RSI、MACD、Bollinger Bands、KD、ATR 等。
* **基本面抓取**：自動抓取 PE (本益比)、殖利率、EPS、ROE、債務比等關鍵數據。
* **多維度評分系統**：根據加權演算法給予 -12 至 +12 分的評價，輔助避開情緒化交易。
* **數據視覺化**：自動生成包含價格、成交量及三大動能指標的 K 線分析圖表。
* **多股競爭排名**：支援同時輸入多檔代碼，系統會依據最終評分進行排序。

---

## 開發流程與環境 (Workflow & Environment)

* **實驗與驗證環境**：**Google Colab** (用於初期利用 Gemini 進行程式碼測試與數據視覺化)。
* **專案重構與整合 IDE**：**Visual Studio Code (VS Code)** (用於最後將程式碼模組化，並透過 Claude 進行架構優化)。
* **程式語言**：Python 3.8+
* **核心套件**：`yfinance`, `pandas`, `matplotlib`, `mplfinance`, `numpy`

---

## 安裝與使用 (Installation & Usage)

### 1.安裝必要套件
請執行以下指令以安裝所需程式庫：
```bash
pip install yfinance mplfinance matplotlib pandas numpy

```

### 2.執行程式
執行 main.py 後，依照提示輸入股票代碼（名稱之間請用逗號隔開）：
```Plaintext
請輸入股票代碼：
> 2330.TW, NVDA, 0050.TW
```
---

## 分析維度與評分原理 (Scoring Principle)
本系統建立了一套多維度加權演算法，總分範圍從 **-12 分至 +12 分**。透過客觀數據計算，幫助使用者避開情緒化交易，並提供量化的買賣參考：

### 1. 技術面評分 (Technical Analysis: Max +6 / Min -6)
技術面專注於市場動能與趨勢跟隨，包含以下判斷指標：
* **趨勢跟隨**：判斷短期 MA5 是否位於 MA20 之上，以及股價是否站穩於季線 (MA60) 上方。
* **動能交叉**：自動偵測 MACD 快慢線交叉狀況，以及 RSI 是否出現超買/超賣後的反轉訊號。
* **支撐壓力**：結合布林通道 (Bollinger Bands) 與 KD 指標，評估當前價位之相對強度。

### 2. 基本面評分 (Fundamental Analysis: Max +6 / Min -6)
基本面專注於公司的獲利能力與財務健康度：
* **獲利估值**：對比歷史 PE (本益比) 水位，評估當前股價是否處於合理區間；檢視 EPS 成長性。
* **財務體質**：分析 ROE (股東權益報酬率) 及債務比率，確保公司具備穩健的經營基石。
* **股利政策**：納入現金殖利率考量，評估長期持有的投資價值。

### 3. 最終評分建議 (Final Conclusion)
系統彙整上述 12 個維度的加權結果後，會給出最終排名與建議：
* **+8 ~ +12 分**：強力建議買入 / 多頭趨勢強勁。
* **+4 ~ +7 分**：偏多看待 / 適合分批佈局。
* **-3 ~ +3 分**：中性觀望 / 市場趨勢不明朗。
* **-4 分以下**：建議避開 / 趨勢疲軟或估值過高。

## 數據視覺化說明 (Visualization Layers)
本系統生成的分析圖表分為五大專業層級，提供全方位的技術面解讀：
1. **價格圖層 (Price Layer)**：
   * 包含 **K線圖**、三條關鍵**均線 (MA5, MA20, MA60)**。
   * 整合 **布林通道 (Bollinger Bands)** 陰影區，直觀呈現股價波動區間與支撐壓力。
2. **量能圖層 (Volume Layer)**：
   * 展示**成交量柱狀圖**，並以顏色（紅漲綠跌）區分每日動能變化。
3. **RSI 強弱層 (RSI Layer)**：
   * 標示 **RSI 指標** 走勢，並清楚劃分 **超買區 (70)** 與 **超賣區 (30)**，輔助判斷反轉時機。
4. **MACD 動能層 (MACD Layer)**：
   * 呈現 **MACD 柱狀圖** 與 **快慢線 (DIF/DEA)**，用於偵測趨勢的增強或衰退。
5. **KD 震盪層 (KD Layer)**：
    透過 **K值與 D值** 的隨機震盪判讀，精確掌握短期的買賣訊號點。

<img width="1283" height="666" alt="Figure_1" src="https://github.com/user-attachments/assets/afc54b5c-1143-4b90-9e78-1ae4d26ec444" />

*<img width="1276" height="821" alt="螢幕擷取畫面 2026-04-19 001913" src="https://github.com/user-attachments/assets/8ffbade9-ab38-49fb-b4c0-673c8cc8bb28" />
*<img width="1283" height="666" alt="2" src="https://github.com/user-attachments/assets/06c4aadc-1720-47c8-b648-2ae2a3e1caa9" />



---
## 授權條款與免責聲明

### 授權條款
本專案採用 **[MIT License](LICENSE)** 授權。您可以自由地使用、修改及分發本程式碼，但須保留原作者之版權聲明。

### 免責聲明 
本工具僅作為「生成式 AI」課程之教學實作與學術研究參考，**不構成任何形式的投資建議或邀約**。 程式抓取之數據源自 Yahoo Finance，數據可能存在延遲或誤差，不保證數據之即時性與精確性。金融市場投資具有高度風險，過往績效不代表未來表現。使用者在進行任何金融決策前，應獨立思考或諮詢專業投資顧問，使用本程式所造成之任何財務損失或法律責任，開發小組成員概不負責。**投資者應自負盈虧責任。**

---
## 小組成員
* **余沛達** (411770265)：AI 邏輯構建、程式初版開發 (Gemini/ChatGPT)
* **蘇靖文** (411770323)：測試數據驗證、程式框架重構 (Claude)、GitHub 版本控管
* **黃國維** (411770364)：環境整合、股票市場分類研究
* **陳芊羽** (411770414)：股票數據分析、技術報告撰寫
  
