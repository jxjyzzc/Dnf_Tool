import os
import sys
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
## parenddir 是当前代码文件所在目录的父目录
parenddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parenddir)
# project_dir = os.path.join(parenddir, "..")
# sys.path.append(project_dir)

from startUI.Bag import Bag
import startUI.startInfoRead as startInfoRead
from startUI.RoleInfo import RoleInfo

__all__ = ['Bag','startInfoRead','RoleInfo']