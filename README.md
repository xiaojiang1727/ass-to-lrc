# ASS TO LRC
[[English](https://github.com/xiaojiang1727/ass-to-lrc/blob/main/README_EN.md)|[[简体中文](https://github.com/xiaojiang1727/ass-to-lrc/blob/main/README.md)]
>一个轻量级、零依赖的 Python 脚本，专门用于将带有\k、\K、\kf 标签的 .ass 字幕转换为增强型 .lrc 歌词文件
- **注意：此脚本为AI生成人工修改并添加详细注释**

## 核心特性
- 逐字时间戳支持：完美解析 ASS 中的 \k、\K、\kf 标签，生成支持逐字高亮的增强型 LRC 格式
- 智能文本清理：自动移除 ASS 标签，并将 \N、\n 换行符转换为平滑的空格
- 高兼容性：自动处理 UTF-8 和 UTF-8 with BOM 编码，避免乱码
- 零依赖：仅使用 Python 标准库，无需安装任何第三方库
## 快速开始
### 方式 A：直接运行 (推荐)
1. 前往 [Releases](https://github.com/xiaojiang1727/ass-to-lrc/releases/) 页面
2. 下载最新的 ass-to-lrc.exe。
3. 双击运行，根据提示操作即可。

### 方式 B：源码运行
1. 确保已安装 Python 3.10+
2. 下载 ass-to-lrc.py
3. 双击运行或在终端执行```python ass_to_lrc.py```根据提示操作即可

## 转换示例
```
输入 (ASS):
Dialogue: 0,0:00:01.00,0:00:03.50,Default,,0,0,0,,{\k10}这{\k20}是{\k30}测{\k40}试{\k150}歌词
输出 (Enhanced LRC):
[00:01.00]<00:01.00>这<00:01.10>是<00:01.30>测<00:01.60>试<00:02.00>歌词<00:03.50>
```
## 技术实现细节
- 正则解析：使用正则表达式提取 ASS 标签与文本块。
- 时间轴计算：将 ASS 的厘秒（Centiseconds）单位精准转换为播放器通用的 LRC 时间格式。
- 鲁棒性处理：
- 自动过滤无效的 Dialogue 行。
- 处理不带卡拉OK标签的普通字幕行，确保通用性。

## 贡献
如果你有任何改进建议（例如支持更复杂的标签解析），欢迎提交 Issue 或 Pull Request！
