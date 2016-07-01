import sys

activate_this = os.path.join(os.environ.get('IHS_APP_DIR'),'../virtenv/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

sys.path.append(os.environ.get('IHS_APP_DIR'))

from app import app as application
