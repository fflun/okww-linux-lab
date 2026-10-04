# OK-WW Linux Lab

云鸣潮 Linux 浏览器适配实验，保留离线识别验证和平台隔离工作。

**当前暂停 Linux 实机路线。本项目不是可直接使用的自动每日工具。**

## 已验证

- 无界面 Chromium 启动、1280×720 合成画面取帧。
- 原版 OK 执行器、CPU OCR 和模板识别的离线运行。
- Windows 专用接口隔离，游戏按键在离线入口中被禁止。

香港实机尝试停在排队，没有取得游戏视频；真实角色识别、战斗、领奖与无人值守均未验收。用户反馈该地区无法使用云鸣潮，本实验没有独立确认其地区限制规则。

## 内容

| 目录 | 用途 |
| --- | --- |
| `code/linux` | 离线测试、只读帧识别、框架补丁 |
| `code/cloud_*.py` | 浏览器设备和传输适配 |
| `capture` | 可见 Chromium 登录和视频帧采集；不自动点击进入游戏 |
| `patches`、`platform` | OK-WW 原任务的平台接口隔离补丁 |
| `VALIDATION.md` | 实测结果与未验证边界 |

不包含游戏素材、OCR 模型、账号、浏览器登录资料、服务器部署文件或私有运行日志。`code/chrome-extension/worker.js` 在离线实验中仅提供取帧函数，没有附带可安装扩展。

## 离线复现

已验证环境为 Debian 13、Python 3.13、Chromium，CPU 推理。需自行准备对应版本的 **[ok-script](https://github.com/ok-oldking/ok-script)** `ok/` 源码与许可证，以及中文 `.ttc` 字体和许可证。框架源码未打包，`framework-source-sha256.json` 记录了实际验证的逐文件散列；不匹配时停止，避免对未知版本直接打补丁。

```sh
python3 prepare_stage.py \
  --framework-source /path/to/ok \
  --framework-license /path/to/ok-script/LICENSE.txt \
  --font /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc \
  --font-license /usr/share/doc/fonts-wqy-zenhei/copyright
python3 -m venv stage/.venv
stage/.venv/bin/python -m pip install -r code/linux/requirements-stage2.lock.txt
sh stage/code/linux/check-runtime.sh
```

系统需提供 `/usr/bin/chromium` 及其依赖。OCR 模型随固定版本的 OCR 包安装。正常测试只打开禁止联网的空白页，生成合成样本；结束后关闭自己创建的浏览器。报告位于 `stage/probe-state/runtime-result.json`。默认入口 `python3 code/main_cloud_linux.py` 只输出状态。

Linux 设备边界测试：

```sh
PYTHONPATH=stage/code:stage/vendor stage/.venv/bin/python -m unittest discover -s code/tests -p test_cloud_linux_device.py
```

## 可见采集与只读识别（实验）

有图形桌面且当地可访问官方服务时，可显式运行 `stage/.venv/bin/python capture/main.py`。它打开独立 Chromium，登录由用户完成，只保存最新视频帧与状态，不执行每日任务。关闭程序会关闭它创建的浏览器；登录资料默认保留在用户目录 `.local/share/okww-linux-lab`，可用 `OKWW_CAPTURE_DIR` 指定专用目录。

在拥有读取权限、已产生视频帧且自行提供 OK-WW 模板素材后：

```sh
PYTHONPATH=stage/code:stage/vendor stage/.venv/bin/python code/linux/live_recognition_probe.py \
  --capture-dir "$HOME/.local/share/okww-linux-lab" \
  --assets /path/to/assets --output /tmp/okww-recognition
```

此入口是有界只读探测，不启动游戏任务。尚未在真实云游戏画面上通过验收。

## 来源

- [OK-WW](https://github.com/ok-oldking/ok-wuthering-waves)：基准 `v3.6.7`，提交 `7df910be3b91e73be0f7a96d34fb4091510f7fac`。项目适配代码和 OK-WW 补丁按 AGPL-3.0 提供，见 `LICENSE`。
- [ok-script](https://github.com/ok-oldking/ok-script)：执行器与识别框架，需另行提供；其自身许可证和附加条款继续适用。
- [March7thAssistant](https://github.com/moesnow/March7thAssistant)：键码映射来源及 GPL-3.0 说明见 `THIRD_PARTY.md`。

项目改动没有替换 OK-WW 的角色轮转、每日流程或战斗主循环。
