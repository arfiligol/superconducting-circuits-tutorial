# Secret Management Plan

最後更新：2026-03-12

本文件定義 migration 期間與 post-migration 的 secret management 最低策略，避免 auth/session 完成後仍依賴預設 secret、明文本地儲存、或無法輪替的 bootstrap 憑證。

## Goals

1. production / shared environments 不得使用預設 secret
2. bootstrap credentials 必須可退役
3. desktop / local runtime 不能把長期 secret 直接落在 plaintext config
4. secret lifecycle 必須可輪替、可失效、可追蹤 owner

## Secret Classes

| Secret | 用途 | 目前位置 | 長期要求 |
|---|---|---|---|
| `SC_SESSION_SECRET` | session signing / auth context | `.env` | production 必須由安全注入提供，禁止預設值 |
| `SC_BOOTSTRAP_ADMIN_PASSWORD` | 初始管理員 bootstrap | `.env` | 僅供 bootstrap 階段使用，完成後必須退役 |
| `SC_RQ_REDIS_URL` 內含憑證時 | queue backend access | `.env` | 視為 secret，禁止直接出現在 logs |
| desktop-local token / credential | desktop app local auth/session | desktop local store | 必須用 OS keychain / secure storage，不可 plaintext |

## Baseline Rules

- `.env.example` 可以保留 placeholder，但 production startup 必須拒絕 `change-me` 類預設值
- `.env`、desktop local secret files、exported credential cache 必須被 `.gitignore` 覆蓋
- secret 值不得出現在 API response、CLI output、worker payload、frontend bundle
- secret 不得進入 structured logs；必要時只能記 redacted marker

## Lifecycle Rules

### Rotation / Renewal

- 每個長期 secret 必須有明確 owner
- 必須定義 rotation trigger：
  - 定期輪替
  - 洩漏疑慮
  - bootstrap 結束
  - desktop device logout / revoke
- rotation 不得只靠人工口頭流程，至少要有書面操作步驟

### Bootstrap Credential Retirement

- `SC_BOOTSTRAP_ADMIN_PASSWORD` 只能用於初始建立第一個管理員或本地開發 bootstrap
- 一旦系統已有正式管理員帳號或正式 auth source，bootstrap password 必須失效或不再被接受
- bootstrap flow 完成後，必須能用測試證明「再次使用 bootstrap password 不會重新取得管理權限」

### Desktop / Local Secret Storage

- Electron / desktop 不得把長期 token 或 session signing secret 存在 plaintext config
- desktop 端應優先使用 OS-provided secure storage：
  - macOS Keychain
  - Windows Credential Manager
  - Linux Secret Service / keyring
- 若暫時只能使用本地檔案，必須明確標註為 development-only，且不得進入 committed repo 或 docs examples

## Verification

至少要能驗證：

- startup 在 production-like mode 拒絕 default secret
- `.env` 與 secret cache 不會進 git
- bootstrap credential 退役後不可再用
- desktop secure storage path 已定義，或 development-only fallback 有明確 guard

## Mapping To Phases

| 階段 | 要求 |
|---|---|
| Phase 4 | startup validation、`.env`/gitignore baseline、bootstrap retirement plan、rotation owner |
| Phase 5B | task / worker payload 不洩漏 secrets |
| Phase 7 | desktop secure storage、rotation operational docs、production sign-off |

## Checklist

- [ ] startup 拒絕 default `SC_SESSION_SECRET`
- [ ] startup 拒絕 production 使用 default `SC_BOOTSTRAP_ADMIN_PASSWORD`
- [ ] `.env` / secret cache / desktop local secret files 已被 `.gitignore` 保護
- [ ] secret owner 與 rotation trigger 已記錄
- [ ] bootstrap admin credential retirement path 已定義
- [ ] bootstrap retirement 有測試或明確驗證步驟
- [ ] desktop secure storage baseline 已定義
- [ ] logging / CLI / API / worker 不輸出 raw secrets
