from pathlib import Path
from django.core.exceptions import SuspiciousFileOperation


def safe_join(base, *paths):
    """
    安全地连接路径，防止目录遍历攻击
    :param base: 基础路径（绝对路径）
    :param paths: 要拼接的路径片段
    :return: 安全拼接后的相对路径（相对于base）
    :raises SuspiciousFileOperation: 如果路径越界
    """
    base_path = Path(base).resolve()  # 转换为绝对路径
    try:
        full_path = base_path.joinpath(*paths).resolve()
        # 检查最终路径是否仍然在基础路径下
        relative_path = full_path.relative_to(base_path)
        return str(relative_path)
    except ValueError:
        # 路径越界时抛出Django安全异常
        raise SuspiciousFileOperation("路径越界，检测到非法目录遍历")
