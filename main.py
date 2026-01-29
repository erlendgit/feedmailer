import sys
from pathlib import Path

# Voeg de project directory toe aan sys.path
project_dir = Path(__file__).parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from feedmailer.app import App

if __name__ == "__main__":
    App().run()