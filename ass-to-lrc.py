import re
import os

def ass_time_to_ms(ass_time: str) -> int:
    r"""
    将 ASS 时间格式转换为毫秒数。

    ASS 时间格式示例: "1:23:45.67" (时:分:秒.百分秒)
    返回: 对应的毫秒数 (整数)
    """
    h, m, s = ass_time.split(':')
    s, cs = s.split('.')
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(cs) * 10


def ms_to_lrc_time(ms: int) -> str:
    r"""
    将毫秒数转换为 LRC 时间格式。

    LRC 时间格式: "MM:SS.xx" (分:秒.百分秒)
    返回: 格式化后的时间字符串
    """
    m = ms // 60000
    s = (ms % 60000) // 1000
    cs = (ms % 1000) // 10
    return f"{m:02d}:{s:02d}.{cs:02d}"


def clean_text(text: str) -> str:
    r"""
    清理文本中 ASS 特有的换行符和标签。

    - 将 ASS 换行符 \N 和 \n 替换为空格
    - 其他 ASS 标签将在调用此函数前被移除
    """
    return text.replace('\\N', ' ').replace('\\n', ' ')


def parse_dialogue_line(line: str) -> str | None:
    r"""
    解析 ASS 文件中的一行 Dialogue 记录，返回增强型 LRC 行字符串。

    处理逻辑：
    1. 提取起始时间、结束时间和文本内容。
    2. 如果文本中不含卡拉OK标签（\k, \K, \kf），则只输出整行时间戳和清理后的文本。
    3. 如果含有卡拉OK标签，则按 {} 分割，解析每个字词的持续时间，生成带有逐字时间戳的 LRC 行。
       - 输出格式: "[行开始时间]字1时间戳字1字2时间戳字2...<行结束时间>"

    返回:
        如果解析成功，返回格式化后的 LRC 行字符串；否则返回 None。
    """
    # 按 ASS 格式分割 Dialogue 行 (最多分割9次，保留最后一个字段完整)
    parts = line.split(',', 9)
    if len(parts) < 10:
        return None

    start_time_ass = parts[1].strip()
    end_time_ass = parts[2].strip()
    text_content = parts[9].strip()

    # 转换时间为毫秒
    start_time_ms = ass_time_to_ms(start_time_ass)
    end_time_ms = ass_time_to_ms(end_time_ass)

    # 情况1：无卡拉OK标签 → 只生成整行时间戳
    if not re.search(r'\\[kK][fo]?\d+', text_content):
        pure_text = re.sub(r'\{.*?\}', '', text_content)  # 移除所有 ASS 标签
        pure_text = clean_text(pure_text)
        return f"[{ms_to_lrc_time(start_time_ms)}]{pure_text}<{ms_to_lrc_time(end_time_ms)}>"

    # 情况2：有卡拉OK标签 → 解析逐字时间戳
    # 用正则按 {} 分割，保留分隔符，以便区分标签和文字
    chunks = re.split(r'(\{.*?\})', text_content)

    lrc_line = ""                # 最终生成的 LRC 行内容
    current_time_ms = start_time_ms   # 当前累计时间（用于计算字词起始）
    word_start_time_ms = current_time_ms  # 当前字词的开始时间

    for chunk in chunks:
        # 处理 ASS 标签块
        if chunk.startswith('{') and chunk.endswith('}'):
            # 匹配卡拉OK标签: \k50, \K50, \kf50 等
            k_match = re.search(r'\\[kK][fo]?(\d+)', chunk)
            if k_match:
                duration_ms = int(k_match.group(1)) * 10
                word_start_time_ms = current_time_ms
                current_time_ms += duration_ms
        # 处理文字块
        elif chunk.strip() or chunk == " ":
            word_text = clean_text(chunk)
            if word_text:
                time_tag = f"<{ms_to_lrc_time(word_start_time_ms)}>"
                lrc_line += f"{time_tag}{word_text}"
                word_start_time_ms = current_time_ms

    # 在行末尾添加结束时间戳
    end_tag = f"<{ms_to_lrc_time(end_time_ms)}>"
    line_start_tag = f"[{ms_to_lrc_time(start_time_ms)}]"
    return f"{line_start_tag}{lrc_line}{end_tag}"


def convert_ass_to_lrc(input_file: str, output_file: str = None) -> None:
    """
    将 ASS 文件转换为 LRC 文件。

    参数:
        input_file: 输入的 ASS 文件路径
        output_file: 输出的 LRC 文件路径，若为 None 则自动生成（同目录下同名 .lrc）
    """
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '.lrc'

    try:
        # 尝试多种编码读取 ASS 文件（优先 UTF-8，失败则尝试 UTF-8 with BOM）
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(input_file, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()

        lrc_output = []
        for line in lines:
            if line.startswith('Dialogue:'):
                lrc_line = parse_dialogue_line(line)
                if lrc_line:
                    lrc_output.append(lrc_line)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lrc_output))

        print(f"\n✅ 转换成功！")
        print(f"📄 输出文件已保存至: {os.path.abspath(output_file)}")

    except Exception as e:
        print(f"\n❌ 转换过程中发生错误: {e}")


if __name__ == "__main__":
    print("=" * 45)
    print("      ASS 转 LRC 歌词转换器 (保留逐字效果)      ")
    print("=" * 45)

    # 循环获取有效的输入文件
    while True:
        # 去除输入时可能附带的首尾引号
        input_path = input("\n👉 请输入 .ass 文件路径 (可直接将文件拖入窗口): ").strip(' \'"')

        if not input_path:
            print("⚠️ 未输入任何内容，请重试。")
            continue

        if not os.path.exists(input_path):
            print(f"❌ 找不到文件 '{input_path}'，请检查路径是否正确。")
            continue

        if not input_path.lower().endswith('.ass'):
            print("⚠️ 警告：该文件似乎不是以 .ass 结尾，但仍将尝试转换。")

        break

    # 获取输出文件名，允许自定义或自动生成
    output_path = input("\n👉 请输入输出的 .lrc 文件路径 (直接按回车键将自动在原目录同名保存): ").strip(' \'"')
    if not output_path:
        output_path = None

    convert_ass_to_lrc(input_path, output_path)

    # 暂停，防止双击运行时窗口立即关闭
    print("\n" + "=" * 45)
    input("按下回车键退出程序...")