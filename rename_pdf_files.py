import fitz
import PyPDF2
from pathlib import Path
import shutil
import re
import os

def clean_filename(title):
    """清理标题，使其适合作为文件名"""
    # 移除或替换不允许在文件名中使用的字符
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        title = title.replace(char, ' - ')
    
    # 替换多个空格为单个空格
    title = re.sub(r'\s+', ' ', title)

    # 处理特殊引号
    title = title.replace('&#39;', "'")
    title = title.replace('⠍', "-")   
    
    # 移除首尾空格
    title = title.strip()
    
    # 限制文件名长度（Windows文件名限制为255字符）
    if len(title) > 200:
        title = title[:200].rsplit(' ', 1)[0]  # 在单词边界截断
    
    # 如果标题为空或太短，使用默认名称
    if len(title) < 3:
        title = "未命名论文"
    
    return title

def extract_title_smart(pdf_path):
    """智能提取PDF标题的函数"""
    
    # 方法1：从元数据获取
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        if metadata.get('title') and len(metadata['title'].strip()) > 5:
            title = metadata['title'].strip()
            doc.close()
            print(f"  → 从元数据获取标题: {title[:50]}...")
            return title
        doc.close()
    except Exception as e:
        print(f"  → 元数据提取失败: {e}")
    
    # 方法2：通过字体大小判断
    try:
        doc = fitz.open(pdf_path)
        first_page = doc[0]
        blocks = first_page.get_text("dict")
        
        title_candidates = []
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    max_font_size = 0
                    y_position = 0
                    
                    for span in line["spans"]:
                        text = span["text"].strip()
                        font_size = span["size"]
                        line_text += text + " "
                        max_font_size = max(max_font_size, font_size)
                        y_position = span["bbox"][1]  # y坐标
                    
                    line_text = line_text.strip()
                    # 标题通常字体较大，位置靠上，长度适中
                    if (len(line_text) > 10 and len(line_text) < 200 and 
                        max_font_size > 12 and y_position < 200):
                        title_candidates.append((line_text, max_font_size, y_position))
        
        if title_candidates:
            # 优先选择字体最大且位置靠上的
            title_candidates.sort(key=lambda x: (-x[1], x[2]))  # 按字体大小降序，位置升序
            title = title_candidates[0][0]
            doc.close()
            print(f"  → 通过字体分析获取标题: {title[:50]}...")
            return title
        
        doc.close()
    except Exception as e:
        print(f"  → 字体分析失败: {e}")
    
    # 方法3：简单文本提取（备选方案）
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            first_page = reader.pages[0]
            text = first_page.extract_text()
            lines = text.split('\n')
            
            for line in lines[:15]:  # 检查前15行
                line = line.strip()
                # 过滤掉全大写行、太短的行、常见的页眉页脚
                if (len(line) > 10 and len(line) < 200 and 
                    not re.match(r'^[A-Z\s]+$', line) and
                    not line.lower().startswith(('abstract', 'keywords', 'introduction', 
                                               'copyright', '©', 'proceedings', 'conference'))):
                    print(f"  → 通过文本提取获取标题: {line[:50]}...")
                    return line
    except Exception as e:
        print(f"  → 文本提取失败: {e}")
    
    print("  → 无法提取标题，使用默认名称")
    return "无法提取标题"

def rename_pdfs_in_place(source_directory=None, backup=True):
    """
    批量提取PDF标题并直接重命名文件
    
    Args:
        source_directory: 源PDF文件夹路径，如果为None则使用当前目录
        backup: 是否备份，True则备份到backup子目录，False则不备份
    """
    # 如果未指定目录，使用当前目录
    if source_directory is None:
        source_path = Path.cwd()
    else:
        source_path = Path(source_directory)
    
    # 检查源目录是否存在
    if not source_path.exists():
        print(f"源目录不存在: {source_path}")
        return
    
    # 如果需要备份，创建backup子目录并复制PDF文件
    if backup:
        backup_path = source_path / "backup"
        
        print(f"正在备份PDF文件...")
        print(f"备份目录: {backup_path}")
        
        if backup_path.exists():
            print(f"警告: 备份目录已存在，将被覆盖")
            shutil.rmtree(backup_path)
        
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # 只复制PDF文件到备份目录
        pdf_files_to_backup = list(source_path.glob("*.pdf"))
        for pdf_file in pdf_files_to_backup:
            shutil.copy2(pdf_file, backup_path / pdf_file.name)
        
        print(f"✓ 备份完成！已备份 {len(pdf_files_to_backup)} 个PDF文件")
        print("-" * 60)
    else:
        print(f"跳过备份（backup=False）")
        print("-" * 60)
    
    # 获取所有PDF文件
    pdf_files = list(source_path.glob("*.pdf"))
    
    if not pdf_files:
        print("在源目录中没有找到PDF文件！")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    print(f"工作目录: {source_path}")
    print("-" * 60)
    
    results = []
    success_count = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] 处理: {pdf_file.name}")
        
        try:
            # 提取标题
            title = extract_title_smart(pdf_file)
            
            # 清理标题作为文件名
            clean_title = clean_filename(title)
            new_filename = f"{clean_title}.pdf"
            
            # 检查目标文件是否已存在，如果存在则添加序号
            new_file_path = source_path / new_filename
            counter = 1
            original_new_filename = new_filename
            
            # 如果新文件名和原文件名相同，跳过重命名
            if pdf_file.name == new_filename:
                print(f"  → 文件名已是标题格式，跳过")
                results.append({
                    'original_name': pdf_file.name,
                    'new_name': new_filename,
                    'title': title,
                    'status': 'skipped (already correct)'
                })
                success_count += 1
                continue
            
            while new_file_path.exists():
                name_without_ext = original_new_filename[:-4]  # 移除.pdf
                new_filename = f"{name_without_ext} ({counter}).pdf"
                new_file_path = source_path / new_filename
                counter += 1
            
            # 重命名文件
            pdf_file.rename(new_file_path)
            
            results.append({
                'original_name': pdf_file.name,
                'new_name': new_filename,
                'title': title,
                'status': 'success'
            })
            
            success_count += 1
            print(f"  ✓ 成功重命名为: {new_filename}")
            
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            results.append({
                'original_name': pdf_file.name,
                'new_name': '',
                'title': '',
                'status': f'error: {e}'
            })
    
    # 生成处理报告
    generate_report(results, source_path, success_count, len(pdf_files))

def generate_report(results, target_path, success_count, total_count):
    """生成处理报告"""
    
    report_path = target_path / "处理报告.txt"
    
    print(f"\n" + "="*60)
    print(f"处理完成！")
    print(f"成功处理: {success_count}/{total_count} 个文件")
    print(f"报告已保存至: {report_path}")
    print("="*60)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("PDF标题提取和重命名处理报告\n")
        f.write("="*50 + "\n\n")
        f.write(f"处理时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总文件数: {total_count}\n")
        f.write(f"成功处理: {success_count}\n")
        f.write(f"失败数量: {total_count - success_count}\n\n")
        
        f.write("详细结果:\n")
        f.write("-"*50 + "\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"\n{i}. 原文件名: {result['original_name']}\n")
            if result['status'] == 'success' or 'skipped' in result['status']:
                f.write(f"   新文件名: {result['new_name']}\n")
                f.write(f"   提取标题: {result['title']}\n")
                f.write(f"   状态: {result['status']}\n")
            else:
                f.write(f"   状态: {result['status']}\n")

# 主函数
def main():
    """主函数 - 使用示例"""
    
    # 设置源目录
    source_dir = input("请输入PDF文件所在目录路径（留空使用当前目录）: ").strip().strip('"')
    
    # 如果输入为空，使用None（表示当前目录）
    if not source_dir:
        source_dir = None
        print("将使用当前目录")
    else:
        # 检查源目录是否存在
        if not os.path.exists(source_dir):
            print("源目录不存在！")
            return
    
    # 询问是否需要备份
    backup_choice = input("是否需要备份PDF文件? (y/n，默认y): ").strip().lower()
    need_backup = backup_choice != 'n'
    
    print(f"\n开始处理...")
    if need_backup:
        print(f"将创建backup子目录并备份所有PDF文件")
    else:
        print(f"不进行备份")
    print(f"然后直接对文件进行重命名")
    
    confirm = input("\n确认继续? (y/n): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 执行批量处理
    rename_pdfs_in_place(source_dir, backup=need_backup)

if __name__ == "__main__":
    # 直接调用示例（你可以直接修改这里的路径）
    
    # # 方式1: 交互式输入
    # main()
    
    # 方式2: 直接指定路径和备份选项
    # source_directory = None  # None表示当前目录，或者指定具体路径如 r"papers"
    # rename_pdfs_in_place(source_directory, backup=True)  # backup=True表示备份，False表示不备份
    
    # 方式3: 处理当前目录，不备份
    rename_pdfs_in_place(backup=False)