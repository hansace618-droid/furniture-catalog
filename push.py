#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
家具文案库一键推送脚本
用法: python push.py  (Windows)
      python3 push.py (Mac/Linux)
功能: 读取 template.csv -> 生成 data.js -> 推送到 GitHub
"""

import csv
import json
import os
import subprocess
import sys
from datetime import datetime

# Windows 控制台编码修复
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_data():
    """读取 CSV，按型号分组，生成结构化数据"""
    csv_path = os.path.join(SCRIPT_DIR, "template.csv")
    if not os.path.exists(csv_path):
        print("[错误] 找不到 template.csv，请确认文件在脚本同目录下")
        sys.exit(1)

    # 自动检测编码（Excel 在中文 Windows 上默认存 GBK）
    with open(csv_path, "rb") as f:
        raw = f.read()

    encoding = None
    for enc in ["utf-8-sig", "utf-8", "gb18030", "gbk"]:
        try:
            raw.decode(enc)
            encoding = enc
            break
        except (UnicodeDecodeError, ValueError):
            continue

    if encoding is None:
        print("[错误] 无法识别 CSV 编码，请用 UTF-8 或 GBK 保存")
        sys.exit(1)

    print(f"   编码: {encoding}")

    import io
    products = {}  # model -> product dict
    product_order = []  # 保持 CSV 中的顺序

    with io.StringIO(raw.decode(encoding)) as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = (row.get("型号") or "").strip()
            if not model:
                continue

            if model not in products:
                image_file = (row.get("图片文件名") or "").strip()
                image_path = f"images/{image_file}" if image_file else ""
                products[model] = {
                    "model": model,
                    "image": image_path,
                    "product_name": (row.get("产品名称") or "").strip(),
                    "copies": []
                }
                product_order.append(model)

            copy = {
                "copy_cn": (row.get("文案中文") or "").strip(),
                "copy_en": (row.get("文案英文") or "").strip(),
                "tags": (row.get("标签") or "").strip()
            }
            # 只要有中文或英文文案就保留
            if copy["copy_cn"] or copy["copy_en"]:
                products[model]["copies"].append(copy)

    data = {"products": [products[m] for m in product_order]}
    return data


def write_data_js(data):
    """写出 data.js（供 index.html 直接加载）"""
    output_path = os.path.join(SCRIPT_DIR, "data.js")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("const CATALOG_DATA = ")
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(";\n")
    total_copies = sum(len(p["copies"]) for p in data["products"])
    print(f"✅ data.js 已生成: {len(data['products'])} 个产品, {total_copies} 条文案")


def git_push():
    """git add -> commit -> push"""
    os.chdir(SCRIPT_DIR)

    def run_git(args):
        """运行 git 命令，处理 Windows 编码问题"""
        return subprocess.run(
            ["git"] + args,
            capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )

    # 检查是否 git 仓库
    r = run_git(["rev-parse", "--is-inside-work-tree"])
    if r.returncode != 0:
        print("[!] 当前目录不是 git 仓库，请先初始化:")
        print("    git init")
        print("    git remote add origin https://github.com/hansace618-droid/furniture-catalog.git")
        return False

    run_git(["add", "."])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"update catalog {timestamp}"

    r = run_git(["commit", "-m", commit_msg])
    out = (r.stdout or "") + (r.stderr or "")
    if "nothing to commit" in out or "no changes" in out:
        print("[!] 没有变更，跳过提交")
        return True

    if r.returncode != 0:
        print(f"[!] commit 出错: {out}")
        return False

    r = run_git(["push"])
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(f"[!] push 出错: {out}")
        print("[?] 如果是认证问题，请配置 git 凭证或 SSH key")
        return False

    print("[OK] 已推送到 GitHub!")
    print("    https://hansace618-droid.github.io/furniture-catalog/")
    return True


def main():
    print("=" * 50)
    print("  家具文案库 - 一键推送")
    print("=" * 50)

    print("\n[1/3] 读取 template.csv ...")
    data = build_data()

    print("[2/3] 生成 data.js ...")
    write_data_js(data)

    print("[3/3] 推送到 GitHub ...")
    git_push()

    print("\n[完成] 全部搞定!\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")  # Windows 防止窗口闪退
