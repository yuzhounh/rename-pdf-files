import fitz
from pathlib import Path
import re

def clean_filename(title):
    """Clean title to make it suitable as a filename"""
    # Remove or replace characters not allowed in filenames
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        title = title.replace(char, ' - ')
    
    # Replace multiple spaces with single space
    title = re.sub(r'\s+', ' ', title)

    # Handle special quotes
    title = title.replace('&#39;', "'")
    title = title.replace('⠍', "-")   
    
    # Remove leading and trailing spaces
    title = title.strip()
    
    # Limit filename length (Windows filename limit is 255 characters)
    if len(title) > 200:
        title = title[:200].rsplit(' ', 1)[0]  # Truncate at word boundary
    
    # If title is empty or too short, use default name
    if len(title) < 3:
        title = "Untitled Paper"
    
    return title

def extract_title_from_metadata(pdf_path):
    """Extract title from PDF metadata"""
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        if metadata.get('title') and len(metadata['title'].strip()) > 5:
            title = metadata['title'].strip()
            doc.close()
            print(f"  → Title extracted from metadata: {title[:50]}...")
            return title
        doc.close()
    except Exception as e:
        print(f"  → Metadata extraction failed: {e}")
    
    print("  → Unable to extract title from metadata")
    return None

def rename_pdfs_in_place(source_directory=None):
    """
    Batch extract PDF titles and rename files directly
    
    Args:
        source_directory: Source PDF folder path, uses current directory if None
    """
    # If no directory specified, use current directory
    if source_directory is None:
        source_path = Path.cwd()
    else:
        source_path = Path(source_directory)
    
    # Check if source directory exists
    if not source_path.exists():
        print(f"Source directory does not exist: {source_path}")
        return
    
    # Get all PDF files
    pdf_files = list(source_path.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in source directory!")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    print(f"Working directory: {source_path}")
    print("-" * 60)
    
    results = []
    success_count = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        
        try:
            # Extract title from metadata
            title = extract_title_from_metadata(pdf_file)
            
            # If unable to extract title, skip this file
            if title is None:
                print(f"  → Skipping file (unable to extract title)")
                results.append({
                    'original_name': pdf_file.name,
                    'new_name': '',
                    'title': '',
                    'status': 'skipped (no title in metadata)'
                })
                continue
            
            # Clean title as filename
            clean_title = clean_filename(title)
            new_filename = f"{clean_title}.pdf"
            
            # Check if target file already exists, add counter if it does
            new_file_path = source_path / new_filename
            counter = 1
            original_new_filename = new_filename
            
            # If new filename is same as original filename, skip renaming
            if pdf_file.name == new_filename:
                print(f"  → Filename already in title format, skipping")
                results.append({
                    'original_name': pdf_file.name,
                    'new_name': new_filename,
                    'title': title,
                    'status': 'skipped (already correct)'
                })
                success_count += 1
                continue
            
            while new_file_path.exists():
                name_without_ext = original_new_filename[:-4]  # Remove .pdf
                new_filename = f"{name_without_ext} ({counter}).pdf"
                new_file_path = source_path / new_filename
                counter += 1
            
            # Rename file
            pdf_file.rename(new_file_path)
            
            results.append({
                'original_name': pdf_file.name,
                'new_name': new_filename,
                'title': title,
                'status': 'success'
            })
            
            success_count += 1
            print(f"  ✓ Successfully renamed to: {new_filename}")
            
        except Exception as e:
            print(f"  ✗ Processing failed: {e}")
            results.append({
                'original_name': pdf_file.name,
                'new_name': '',
                'title': '',
                'status': f'error: {e}'
            })
    
    # Generate processing report
    generate_report(results, source_path, success_count, len(pdf_files))

def generate_report(results, target_path, success_count, total_count):
    """Generate processing report"""
    
    report_path = target_path / "Processing_Report.txt"
    
    print(f"\n" + "="*60)
    print(f"Processing complete!")
    print(f"Successfully processed: {success_count}/{total_count} files")
    print(f"Report saved to: {report_path}")
    print("="*60)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("PDF Title Extraction and Renaming Report\n")
        f.write("="*50 + "\n\n")
        f.write(f"Processing time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total files: {total_count}\n")
        f.write(f"Successfully processed: {success_count}\n")
        f.write(f"Failed: {total_count - success_count}\n\n")
        
        f.write("Detailed results:\n")
        f.write("-"*50 + "\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"\n{i}. Original filename: {result['original_name']}\n")
            if result['status'] == 'success' or 'skipped' in result['status']:
                f.write(f"   New filename: {result['new_name']}\n")
                f.write(f"   Extracted title: {result['title']}\n")
                f.write(f"   Status: {result['status']}\n")
            else:
                f.write(f"   Status: {result['status']}\n")

if __name__ == "__main__":
    # Process current directory directly, no backup, no interaction
    rename_pdfs_in_place()