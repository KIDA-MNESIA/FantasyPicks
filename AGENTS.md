## 当前索引

| App | 上游仓库 | IPA 匹配规则 |
| --- | --- | --- |
| Aidoku | `Aidoku/Aidoku` | `^Aidoku\.ipa$` |
| Venera | `haukuen/venera` | `^venera-ios-.*\.ipa$` |
| PiliPlus | `bggRGjQaUbCoE/PiliPlus` | `^PiliPlus_ios_.*\.ipa$` |
| Feather | `claration/Feather` | `^Feather\.ipa$` |
| FluxDO | `Lingyan000/fluxdo` | `(?:.*ios.*\|fluxdo.*)\.ipa$` |
| Simple Live | `June6699/dart_simple_live` | `^ios_no_sign\.ipa$` |
| Reynard Browser | `minh-ton/reynard-browser` | `^Reynard\.ipa$` |
| Mangayomi | `kodjodevf/mangayomi` | `^Mangayomi-.*-ios\.ipa$` |
| Anx Reader | `Anxcye/anx-reader` | `^Anx-Reader-ios-.*-unsigned\.ipa$` |
| NipaPlay-Reload | `AimesSoft/NipaPlay-Reload` | `^NipaPlay_.*_iOS_arm64\.ipa$` |
| Kazumi | `Predidit/Kazumi` | `^Kazumi_ios_.*_no_sign\.ipa$` |
| Spotube | `team-spotube/spotube` | `^Spotube-iOS\.ipa$` |
| Kelivo | `Chevey339/kelivo` | `^Kelivo_ios_.*\.ipa$` |
| v2Explore | `xinghelee/v2ex` | `^V2EX-.*-unsigned\.ipa$` |
| iTorrent | `XITRIX/iTorrent` | `^iTorrent\.ipa$` |
| qBitControl | `Michael-128/qBitControl` | `^qBitControl\.ipa$` |
| PPSSPP | `hrydgard/ppsspp` | `^PPSSPP-iOS-v[0-9.]+\.ipa$` |
| LiveContainer | `LiveContainer/LiveContainer` | `^LiveContainer\.ipa$` |
| StikDebug | `StikDebug/StikDebug` | `^StikDebug-[0-9.]+\.ipa$` |
| UTM SE | `utmapp/UTM` | `^UTM-SE\.ipa$` |

## 文件说明

- `source.json`：AltStore 读取的软件源文件。
- `apps.json`：精选收录的上游 GitHub IPA 项目清单。
- `scripts/update_altstore_source.py`：自动检查上游 GitHub Releases 并更新 `source.json`。
- `.github/workflows/update-source.yml`：GitHub Actions 每日定时更新任务。
- `index.html`：GitHub Pages 首页，包含一键添加到 AltStore 的链接。

## 更新机制

GitHub Actions 会每日运行一次 `scripts/update_altstore_source.py`：

1. 读取 `apps.json` 中的上游仓库配置。
2. 扫描最近若干个 GitHub Releases。
3. 只匹配 `.ipa` 资产，下载后读取 `Payload/*.app/Info.plist`。
4. 将版本号、构建号、最小系统版本、下载地址和文件大小写入 `source.json`。
5. 如 `source.json` 有变化，自动提交并推送回仓库。

也可以在 GitHub Actions 页面手动触发 `Update AltStore Source`。

## GitHub Pages

在仓库 `Settings -> Pages` 中启用 GitHub Pages，建议选择从 `main` 分支根目录发布。发布后即可在 AltStore 中添加上方源地址。

## 新增条目维护

- 新增条目默认不跟踪预发布版本，使用精确的 iOS IPA 匹配规则。UTM SE、LiveContainer 独立版与 NipaPlay iOS 包不可与其他变体混用。
- 版本号、构建号和最低系统版本继续读取实际 IPA，不能直接用 Release tag 代替。
- 新增条目的 `appPermissions` 已按首次收录的官方 IPA 核对，包括应用扩展；上游升级如改变权限，应重新核对，不直接复制不同发行渠道或开发分支的声明。
