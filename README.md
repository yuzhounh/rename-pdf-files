# PDF 文件批量重命名工具

## 主要功能

本工具可以批量提取 PDF 文件的标题，并根据提取的标题自动重命名文件。主要特性包括：

1. **智能标题提取**
   - 优先从 PDF 元数据中提取标题
   - 通过字体大小和位置分析识别标题（通常标题字体较大且位置靠上）
   - 从第一页文本内容中提取标题作为备选方案
   - 自动过滤页眉、页脚、摘要等非标题内容

2. **文件名清理**
   - 自动移除文件名中不允许使用的特殊字符（`< > : " / \ | ? *`）
   - 处理特殊引号和字符
   - 限制文件名长度（最大200字符，符合 Windows 系统限制）
   - 自动处理重名文件（添加序号）

3. **安全备份**
   - 支持在处理前自动备份所有 PDF 文件到 `backup` 子目录
   - 可选择是否启用备份功能

4. **处理报告**
   - 自动生成详细的处理报告（保存为 `处理报告.txt`）
   - 记录每个文件的重命名结果和状态

## 使用方法

### 环境要求

- Python 3.6 或更高版本
- 所需依赖库：
  - `PyMuPDF` (fitz)
  - `PyPDF2`

### 安装依赖

```bash
pip install PyMuPDF PyPDF2
```

### 使用方式

#### 方式1：交互式运行（推荐）

直接运行脚本，按提示输入：

```bash
python rename_pdf_files.py
```

运行后会提示：
1. 输入 PDF 文件所在目录路径（留空则使用当前目录）
2. 选择是否需要备份（默认是）
3. 确认后开始处理

#### 方式2：修改代码直接运行

编辑 `rename_pdf_files.py` 文件，在文件末尾修改：

```python
# 处理指定目录，启用备份
source_directory = r"D:\Papers"  # 替换为你的PDF文件夹路径
rename_pdfs_in_place(source_directory, backup=True)

# 或处理当前目录，不备份
rename_pdfs_in_place(backup=False)
```

#### 方式3：在代码中调用函数

```python
from rename_pdf_files import rename_pdfs_in_place

# 处理指定目录
rename_pdfs_in_place(r"D:\Papers", backup=True)

# 处理当前目录
rename_pdfs_in_place(backup=False)
```

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
   - 如果启用了备份，原文件会保存在 `backup` 子目录中
   - 处理报告保存在 `处理报告.txt` 文件中

### 注意事项

- 建议首次使用时启用备份功能，确保数据安全
- 如果提取的标题为空或太短（少于3个字符），会使用默认名称"未命名论文"
- 如果无法提取标题，文件名会保持原样或使用"无法提取标题"
- 如果新文件名已存在，会自动添加序号，如：`标题 (1).pdf`、`标题 (2).pdf`

## 联系方式

**Jing Wang**  
Email: wangjing@xynu.edu.cn

---

如有问题或建议，欢迎联系！

