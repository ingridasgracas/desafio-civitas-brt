"""Pipeline BRT - Módulo de fluxos Prefect"""

import os
import sys
from pathlib import Path

# Adiciona diretório raiz ao PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)

# Adiciona diretório de scripts ao PYTHONPATH
scripts_dir = str(Path(__file__).parent.parent / 'scripts')
sys.path.insert(0, scripts_dir)