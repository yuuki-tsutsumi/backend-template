import importlib
import os
import pkgutil

package_dir = os.path.dirname(__file__)

for module_info in pkgutil.iter_modules([package_dir]):
    module_name = module_info.name
    if module_name != "base":  # ベースモデルは Alembic に直接関係ないので除外
        importlib.import_module(f"{__name__}.{module_name}")
