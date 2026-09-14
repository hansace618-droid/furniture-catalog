# 家具文案产品库

## 使用方法

### 首次设置
1. 把图片放到 `images/` 文件夹，按型号命名（如 `CAB001.jpg`）
2. 在 `template.csv` 中填写数据
3. 运行 `python3 push.py` 推送到 GitHub
4. 打开 https://hansace618-droid.github.io/furniture-catalog/

### 日常新增
1. 新图片放入 `images/` 文件夹
2. 在 `template.csv` 新增一行
3. 运行 `python3 push.py`

### 增量补充文案
同一型号可以写多行，每行一条文案。只需填写型号 + 文案内容，图片留空即可。

## CSV 格式说明
| 列名 | 说明 | 必填 |
|------|------|------|
| 型号 | 产品唯一编号，如 CAB001 | ✅ |
| 图片文件名 | images/ 里的文件名，如 CAB001.jpg。同型号后续行留空 | 首行必填 |
| 产品名称 | 中文名称 | ✅ |
| 文案中文 | ins 中文文案 | ✅ |
| 文案英文 | ins 英文文案 | ✅ |
| 标签 | #话题 格式，空格分隔 | 可选 |

## 修改密码
打开 `index.html`，找到 `PWD_KEY` 那行：
```
在浏览器控制台输入 btoa("你的新密码") 获取编码值，替换 PWD_KEY 的值
```
