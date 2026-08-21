# 树莓派 4 配置备份 (Pi 4 + ILI9486 SPI 屏)

本仓库备份树莓派的定制配置，用于迁移/恢复。

## 硬件
- Raspberry Pi 4 Model B (arm64, Debian 13 trixie)
- 3.5 寸 ILI9486 SPI 屏 (waveshare35b-v2, rotate=270)

## 配置内容

### boot/cmdline.txt — 屏幕黑底绿字
ILI9486 屏存在硬件颜色通道映射错误：**屏显示 = (255-G, 255-B, 255-R)**（反相 + RGB 循环错位）。
`vt.default_*` 调色板已全部替换为**补偿值**：背景写白→显黑，文字写黄→显绿。
原配置备份在 `/boot/firmware/cmdline.txt.pre-green`。

### boot/config.txt — 屏驱动
`dtoverlay=waveshare35b-v2,rotate=270` + SPI 启用。

### dotfiles/bash_profile — SSH 会话实时镜像到屏幕
- tty1（物理屏）：保持空闲，作为展示屏
- SSH 交互登录：`exec script -q -f /dev/tty1`，整个会话（输入回显+输出+交互程序）实时镜像到屏幕
- 效果：WindTerm 等 SSH 客户端敲命令，树莓派屏幕实时同步显示，客户端外观不受影响

### dotfiles/bashrc — 同步辅助命令
- `命令 | toscreen`：仅转发 stdout 到屏幕
- `mirror 命令 参数...`：stdout+stderr 转发到屏幕
- 全局版位于 `/etc/bash.bashrc` 末尾

## 恢复方法
```bash
cp boot/cmdline.txt /boot/firmware/cmdline.txt
cp boot/config.txt  /boot/firmware/config.txt
cp dotfiles/bash_profile ~/.bash_profile
cp dotfiles/bashrc ~/.bashrc
# 然后重启
```

## 认证方式
- SSH 密钥推送：git@github.com:shishenshashen/pi-config.git (已配置)

