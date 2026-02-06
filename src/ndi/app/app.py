from ..documentservice import DocumentService
import platform
import sys
import subprocess

class App(DocumentService):
    def __init__(self, session, name='generic'):
        super().__init__()
        self.session = session
        self.name = name

    def var_app_name(self):
        # In Python, any string can be a variable name, so we just return the name
        return self.name

    def version_url(self):
        try:
            # Using subprocess to call git, assuming it's in the path
            # A more robust solution might use a library like GitPython
            v = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
            url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], text=True).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            v = 'unknown'
            url = 'unknown'
        return v, url

    def search_query(self):
        return {
            'base.session_id': self.session.id(),
            'app.name': self.var_app_name()
        }

    def new_document(self):
        os_version = '.'.join(platform.release().split('.'))
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        version, url = self.version_url()

        app_data = {
            'app.name': self.name,
            'app.version': version,
            'app.url': url,
            'app.os': platform.system(),
            'app.os_version': os_version,
            'app.interpreter': 'Python',
            'app.interpreter_version': python_version
        }

        return self.session.new_document('app', **app_data)
