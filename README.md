# PDF 文件批量重命名工具

[![License: MIT](https://img.shields.io/badge/License-MIT-D4A017.svg)](LICENSE)

## 主要功能

本工具可以批量提取 PDF 文件的标题，并根据提取的标题自动重命名文件。主要特性包括：

1. **元数据标题提取**
   - 从 PDF 元数据中提取标题
   - 如果元数据中没有标题，或去除首尾空白后不超过 5 个字符，则跳过该文件

2. **文件名清理**
   - 自动移除文件名中不允许使用的特殊字符（`< > : " / \ | ? *`）
   - 处理特殊引号和字符
   - 限制标题部分长度（最大 200 个字符）
   - 自动处理重名文件（添加序号）

3. **处理报告**
   - 自动生成详细的处理报告（保存为 `Processing_Report.txt`）
   - 记录每个文件的重命名结果和状态

## 使用方法

### 环境要求

- Python 3（具体最低版本取决于所安装的 PyMuPDF 版本）
- 所需依赖库：
  - `PyMuPDF` (fitz)

### 安装依赖

```bash
python -m pip install PyMuPDF
```

### 使用方式

从本仓库下载 `rename_pdf_files.py`，或下载下方说明中的 Windows 可执行文件。脚本处理的是运行命令时的当前目录，且不递归处理子目录。

#### 方式1：直接运行（默认处理当前目录）

直接运行脚本，会自动处理当前目录下的所有 PDF 文件：

```bash
python rename_pdf_files.py
```

#### 方式2：修改代码指定目录

编辑 `rename_pdf_files.py` 文件，在文件末尾修改：

```python
# 处理指定目录
source_directory = r"D:\Papers"  # 替换为你的PDF文件夹路径
rename_pdfs_in_place(source_directory)
```

#### 方式3：在代码中调用函数

```python
from rename_pdf_files import rename_pdfs_in_place

# 处理指定目录
rename_pdfs_in_place(r"D:\Papers")

# 处理当前目录
rename_pdfs_in_place()
```

#### 方式4：使用可执行文件（推荐，无需安装Python）

1. 将 `rename_pdf_files.exe` 与待重命名的 PDF 文件放在同一个目录中
2. 双击运行 `rename_pdf_files.exe`
3. 程序会自动处理该目录下的所有 PDF 文件

**注意**：使用此方式无需安装 Python 或任何依赖库，适合不熟悉 Python 的用户使用。

### 使用示例

1. **准备 PDF 文件**
   - 将要处理的 PDF 文件放在一个文件夹中
   - 确保文件可读且未损坏

2. **运行脚本**
   ```bash
   python rename_pdf_files.py
   ```

3. **查看结果**
   - 文件会被重命名为提取的标题
   - 处理报告保存在 `Processing_Report.txt` 文件中

### 注意事项

- **重要**：本工具会直接重命名文件，不会创建备份。请在使用前确保重要文件已备份
- 仅从 PDF 元数据中提取标题；去除首尾空白后不超过 5 个字符的标题会被跳过
- 通过上述检查的标题在清理后若少于 3 个字符，会使用默认名称 "Untitled Paper"
- 如果无法从元数据提取标题，文件会被跳过，不会重命名
- 如果新文件名已存在，会自动添加序号，如：`标题 (1).pdf`、`标题 (2).pdf`
- 特殊字符处理，如需自定义替换规则，可在代码中修改 `clean_filename` 函数
- 如果 PDF 文件的元数据中没有标题信息，该文件不会被重命名，会在处理报告中标注为"skipped (no title in metadata)"



每次生成报告都会覆盖当前目录中的 `Processing_Report.txt`；需要保留旧报告时，请先另存。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 联系方式

**Jing Wang**  
Email: wangjing@xynu.edu.cn

如有问题或建议，欢迎联系！
