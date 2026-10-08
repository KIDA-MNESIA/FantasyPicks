# FantasyPicks

FantasyPicks 是一个 AltStore 第三方精选索引源，用来索引一些好用的 iOS 侧载应用。

源地址：

```text
https://kida-mnesia.github.io/FantasyPicks/source.json
```

项目仓库：<https://github.com/KIDA-MNESIA/FantasyPicks>

## 收录应用

当前收录 20 个应用，IPA 直接链接到原作者 GitHub Releases。

| 方向 | 应用 |
| --- | --- |
| 阅读 | Aidoku、Venera、Mangayomi、Anx Reader |
| 影音 | PiliPlus、Simple Live、NipaPlay-Reload、Kazumi、Spotube |
| AI | Kelivo |
| 社区 | FluxDO、v2Explore |
| 工具 | Feather、Reynard Browser、iTorrent、qBitControl、LiveContainer、StikDebug |
| 模拟器 | PPSSPP、UTM SE |

完整上游与资产匹配规则见 [apps.json](apps.json)，具体版本和最低系统要求见 [source.json](source.json)。

## 使用说明

- NipaPlay-Reload 需要用户自己的本地或 NAS 媒体资源；qBitControl 需要已部署的 qBittorrent 服务；Kelivo 需要配置相应模型服务。
- iTorrent 普通侧载使用上游支持的 AltStore 或 SideStore。
- LiveContainer 收录独立版，请先阅读[官方安装说明](https://livecontainer.github.io/docs/installation)并完成证书配置；StikDebug 需要配对文件、回环 VPN 和满足调试条件的目标应用。
- PPSSPP 的 JIT 为可选能力；UTM SE 无需 JIT，但解释执行性能有限。游戏文件和系统镜像由用户自行准备。
- 本源直接引用上游 IPA；安装后的扩展和系统能力取决于设备、系统版本及签名方式。

GitHub Actions 每日检查上游发行并更新软件源，也可以手动运行 `Update AltStore Source`。新增条目的版本与权限已按官方发行包核对，后续权限变化需同步维护。
