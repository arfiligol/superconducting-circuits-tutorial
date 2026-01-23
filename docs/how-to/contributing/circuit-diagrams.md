# 貢獻指南：繪製電路圖 (Contributing Circuit Diagrams)

本指南說明如何為專案新增或修改電路圖。我們使用 **Schemdraw** (Python) 來確保電路圖風格一致且可維護。

## 工作流概覽

1.  **編寫腳本**：在 `scripts/docs/` 下創建 Python 腳本來繪製電路。
2.  **生成圖片**：執行腳本，將 SVG 輸出至 `docs/assets/`。
3.  **嵌入文檔**：在 Markdown 中引用圖片並附上原始碼。

## 詳細步驟

### 1. 安裝工具
確保您已安裝 `schemdraw`：
```bash
uv add schemdraw
```

### 2. 編寫繪圖腳本
請將腳本放在 `scripts/docs/` 目錄下。命名應具描述性，例如 `generate_lc_schematic.py`。

**範例樣板**：
```python
import schemdraw
import schemdraw.elements as elm

# 設定輸出路徑
OUTPUT_PATH = 'docs/assets/my_circuit.svg'

def draw():
    d = schemdraw.Drawing()
    
    #在此繪製你的電路
    d += elm.SourceSin().up().label('Port')
    d += elm.Inductor().right().label('L')
    d += elm.Capacitor().down().label('C')
    d += elm.Ground()
    
    # 儲存檔案
    d.save(OUTPUT_PATH)
    print(f"Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    draw()
```

### 3. 生成圖片
在專案根目錄執行腳本：
```bash
uv run scripts/docs/generate_lc_schematic.py
```
檢查 `docs/assets/` 是否出現了 SVG 檔案。

### 4. 嵌入 MkDocs
在您的 Markdown 文件中，請使用以下格式。我們使用 `??? quote` 來建立一個可摺疊的區塊，既展示代碼又不佔用版面。

```markdown
![Circuit Name](../assets/my_circuit.svg)

??? quote "繪製此圖的程式碼（Schemdraw）"
    ```python
    import schemdraw
    import schemdraw.elements as elm

    d = schemdraw.Drawing()
    d += elm.SourceSin().up().label('Port')
    d += elm.Inductor().right().label('L')
    d += elm.Capacitor().down().label('C')
    d += elm.Ground()
    d.save('my_circuit.svg')
    ```
```

## 為什麼要這樣做？

*   **一致性**：所有圖表風格統一。
*   **Vector Graphics**：SVG 在任何解析度下都清晰。
*   **可維護性**：未來的貢獻者可以直接複製代碼來修改電路（例如更改數值），而不需要重畫。
