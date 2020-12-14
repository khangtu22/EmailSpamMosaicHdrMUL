import os

from spam import settings

name_list_file = 'list.txt'
path = os.path.join(settings.MEDIA_ROOT, name_list_file)
print(path)