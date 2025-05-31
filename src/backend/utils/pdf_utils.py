import PyPDF2
from typing import Dict, Any, List, Optional
import re

def extract_pdf_info(file_path: str) -> Dict[str, Any]:
    """
    从PDF文件中提取基本信息
    """
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # 提取元数据
            metadata = reader.metadata
            
            # 提取文本内容
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            # 尝试提取标题
            title = extract_title(metadata, text)
            
            # 尝试提取作者
            authors = extract_authors(metadata, text)
            
            # 尝试提取DOI
            doi = extract_doi(text)
            
            # 尝试提取出版信息
            publication_info = extract_publication_info(text)
            
            return {
                "title": title,
                "authors": authors,
                "doi": doi,
                "publication_info": publication_info,
                "page_count": len(reader.pages),
                "metadata": {k: str(v) for k, v in metadata.items()} if metadata else {}
            }
    except Exception as e:
        print(f"PDF信息提取失败: {e}")
        return {}

def extract_title(metadata: Dict[str, Any], text: str) -> Optional[str]:
    """
    从PDF元数据和文本中提取标题
    """
    # 尝试从元数据中获取
    if metadata and metadata.get('/Title'):
        return metadata.get('/Title')
    
    # 尝试从文本中提取
    lines = text.split('\n')
    if lines and len(lines) > 0:
        # 通常标题是第一行或前几行中最长的一行
        potential_titles = [line.strip() for line in lines[:5] if len(line.strip()) > 10]
        if potential_titles:
            return potential_titles[0]
    
    return None

def extract_authors(metadata: Dict[str, Any], text: str) -> List[str]:
    """
    从PDF元数据和文本中提取作者
    """
    authors = []
    
    # 尝试从元数据中获取
    if metadata and metadata.get('/Author'):
        author_text = metadata.get('/Author')
        # 尝试分割作者名
        authors = [a.strip() for a in re.split(r',|;|and', author_text) if a.strip()]
    
    # 如果元数据中没有作者信息，尝试从文本中提取
    if not authors:
        # 寻找常见的作者行模式
        author_patterns = [
            r'(?i)authors?[:：](.+?)(?:\n|$)',
            r'(?i)by (.+?)(?:\n|$)'
        ]
        
        for pattern in author_patterns:
            matches = re.search(pattern, text[:1000])  # 只在前1000个字符中搜索
            if matches:
                author_text = matches.group(1)
                authors = [a.strip() for a in re.split(r',|;|and', author_text) if a.strip()]
                break
    
    return authors

def extract_doi(text: str) -> Optional[str]:
    """
    从文本中提取DOI
    """
    doi_pattern = r'(?i)(?:doi|DOI)[:：]\s*(10\.\d{4,}(?:\.\d+)*\/\S+)'
    match = re.search(doi_pattern, text)
    if match:
        return match.group(1)
    
    # 尝试直接匹配DOI格式
    doi_direct_pattern = r'(10\.\d{4,}(?:\.\d+)*\/\S+)'
    match = re.search(doi_direct_pattern, text)
    if match:
        return match.group(1)
    
    return None

def extract_publication_info(text: str) -> Dict[str, Any]:
    """
    从文本中提取出版信息
    """
    publication_info = {}
    
    # 尝试提取期刊/会议名称
    journal_patterns = [
        r'(?i)journal[:：]\s*(.+?)(?:\n|$)',
        r'(?i)conference[:：]\s*(.+?)(?:\n|$)',
        r'(?i)proceedings of\s+(.+?)(?:\n|$)'
    ]
    
    for pattern in journal_patterns:
        match = re.search(pattern, text)
        if match:
            publication_info["venue"] = match.group(1).strip()
            break
    
    # 尝试提取年份
    year_pattern = r'(?:©|\(c\)|\b(?:19|20)\d{2}\b)'
    match = re.search(year_pattern, text)
    if match:
        year = match.group(0)
        if year.startswith('©') or year.startswith('(c)'):
            year = re.search(r'\d{4}', year)
            if year:
                year = year.group(0)
        publication_info["year"] = year
    
    # 尝试提取卷号和页码
    volume_pattern = r'(?i)vol(?:ume)?\.?\s*(\d+)'
    match = re.search(volume_pattern, text)
    if match:
        publication_info["volume"] = match.group(1)
    
    pages_pattern = r'(?i)(?:pages|pp)\.?\s*(\d+)[-–](\d+)'
    match = re.search(pages_pattern, text)
    if match:
        publication_info["pages"] = f"{match.group(1)}-{match.group(2)}"
    
    return publication_info