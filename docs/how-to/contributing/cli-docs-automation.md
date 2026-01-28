---
aliases:
  - "CLI 文件自動生成"
  - "CLI Docs Automation"
tags:
  - diataxis/how-to
  - status/draft
  - audience/contributor
  - topic/cli
  - topic/documentation
  - sot/true
owner: I-LI CHIU
---

# CLI 文件自動生成

本文件定義 **CLI Reference 自動化產生** 的整合方式與維護規範。

## 現況

`docs/reference/cli/` 採用 **手寫內容 + 自動生成區塊** 的混合模式。CLI Help 由自動化產生，並同步到手寫文件中，以避免參數與實作不一致。

## 目標

- 以 CLI 的 help 輸出作為單一來源
- 自動產生 `docs/reference/cli/generated/*.md`（不加入導覽與渲染）
- 將 help 區塊同步到手寫的 CLI Reference（保留人類可讀內容）

## 整合規則

1. **產生來源**：從各 CLI 指令的 `--help` 輸出生成 help 區塊。
2. **生成位置**：`docs/reference/cli/generated/`（不加入導航）。
3. **同步方式**：將 generated 的 help 區塊寫入手寫文件中的 `CLI Help（自動生成）` 區段。
4. **更新時機**：新增/變更 CLI 參數後必須重新生成並同步。

## 使用方式

1. 產生 generated 檔案：

```bash
uv run sc-docs-cli --output-dir docs/reference/cli/generated --overwrite
```

2. 同步 help 區塊到手寫文件：

```bash
uv run sc-docs-cli-sync
```

3. 檢查一致性（CI 可用）：

```bash
uv run sc-docs-cli-sync --check
```

!!! note "渲染規則"
    `docs/reference/cli/generated/` 只作為自動生成來源，不納入導航與導覽頁。

## Related

- [CLI Reference](../../reference/cli/index.md)

---

## Agent Rule { #agent-rule }

```markdown
## CLI Docs Automation
- **Hybrid Model**: Hand-written content + auto-generated help block.
- **Generate**: `uv run sc-docs-cli --output-dir docs/reference/cli/generated --overwrite`
- **Sync**: `uv run sc-docs-cli-sync`
- **Check**: `uv run sc-docs-cli-sync --check`
- **Rendered Docs**: Do not render `docs/reference/cli/generated/` in nav.
```
