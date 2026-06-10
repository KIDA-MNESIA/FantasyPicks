# FantasyPicks

FantasyPicks 是一个 AltStore 第三方精选索引源，用来索引一些好用的 iOS 旁载应用。

源地址：

```text
https://kida-mnesia.github.io/FantasyPicks/source.json
```

项目仓库：<https://github.com/KIDA-MNESIA/FantasyPicks>

## 当前索引

| App | 上游仓库 | IPA 匹配规则 |
| --- | --- | --- |
| Aidoku | `Aidoku/Aidoku` | `^Aidoku\.ipa$` |
| Venera | `haukuen/venera` | `^venera-ios-.*\.ipa$` |
| PiliPlus | `bggRGjQaUbCoE/PiliPlus` | `^PiliPlus_ios_.*\.ipa$` |
| Feather | `claration/Feather` | `^Feather\.ipa$` |
| FluxDO | `Lingyan000/fluxdo` | `(?:.*ios.*\|fluxdo.*)\.ipa$` |

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

## 合规声明

FantasyPicks 只做“索引型软件源”：`downloadURL` 直接指向原作者 GitHub Releases，不重新托管第三方 IPA 文件。

本源不拥有所列 App 的版权。若作者不希望被收录，请联系仓库维护者移除。
