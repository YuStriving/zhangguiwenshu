from pathlib import Path

def load_prompt(name: str):
    """加载提示词文件
    
    从项目根目录的prompts文件夹中加载指定的提示词文件。
    
    Args:
        name: 提示词文件名（不含扩展名）
        
    Returns:
        str: 提示词文件内容
        
    Raises:
        FileNotFoundError: 如果提示词文件不存在
    """
    # 获取项目根目录路径
    project_root = Path(__file__).parent.parent.parent
    prompt_path = project_root / "prompts" / (name + ".prompt")
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"提示词文件不存在: {prompt_path}")
        
    return prompt_path.read_text(encoding="utf-8")
if __name__ == "__main__":
    print(load_prompt("filter_table_info"))