####
##
##
# pylint: disable=R
# pylint: disable=unused-import               # W0611: Unused import pylintrc (unused-import)
# pylint: disable=missing-function-docstring  # C0116: Missing function or method docstring (missing-function-docstring)
# pylint: disable=empty-docstring             # C0112: Empty function docstring (empty-docstring)
# C0413: Import "from ... import" should be placed at the top of the module (wrong-import-position)

# init-hook="from pylint.config import find_pylintrc; from os.path import dirname; import sys; import os, sys; print( sys.executable ); print( sys.exec_prefix ); print( sys.path ); sys.path.reverse(); print( sys.path ); pylint_path=os.path.dirname(find_pylintrc()); sys.path.insert(0,find_pylintrc()); sys.path.insert(0,pylint_path+'/../Lib'); sys.path.insert(0,pylint_path+'/../lib'); print(sys.path);"
def run():
    init_hook = "import sys; from pylintrc import sys_path; sys.path = sys_path; print(sys.path);"
    from pylint.config import find_pylintrc
    from os.path import dirname
    from os import sep as dir_sep
    from sys import path as sys_path
    from sys import exec_prefix as prefix_path

    pylint_path = dirname(find_pylintrc())
    # prefix_path = sys.exec_prefix
    # print(sys.executable)
    # print(sys.exec_prefix)
    # print(sys_path)
    # print(pylint_path)
    # print(prefix_path)
    # print(pylint_path not in prefix_path)

    # if pylint_path not in prefix_path:
    if not prefix_path.startswith(pylint_path):
        sys_path = (
            [
                p.replace(prefix_path, pylint_path)
                for p in sys_path
                if p.find(prefix_path) >= 0
            ]
            + [
                p.replace(prefix_path, pylint_path + dir_sep + '.venv')
                for p in sys_path
                if p.find(prefix_path) >= 0
            ]
            + sys_path
        )

    return sys_path


if __name__ == "__main__":

    print(run())

else:

    sys_path = run()
    __all__ = ['sys_path']
