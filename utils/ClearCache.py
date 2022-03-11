import os
import shutil

ToClear = ['./song/AppData']


def Clear():
    try:
        for tree in ToClear:
            shutil.rmtree(tree)
            os.mkdir(tree)
            os.system('touch {}/.gitkeep'.format(tree))
    except Exception as e:
        return {'code': -1, 'msg': e}
    return {'code': 200, 'msg': 'Cleared.'}
