# Maintainers Guide

The process for publishing new versions of this library is the following:

1. Update the version number in `setup.py`
2. [Generate distribution archives](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives)
   1. `pip install --upgrade build`
   2. `python -m build`
3. [Upload distribution archives](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives)
   1. `pip install --upgrade twine`
   2. `twine upload dist/*`
4. Publish the tag
   1. git tag -a "0.X" -m "Release 0.X"
   2. git push --tags
5. Publish the release
   1. Go to [https://github.com/czue/celery-progress/releases/new](https://github.com/czue/celery-progress/releases/new)
   2. Create a release from the tag you just added.
   3. Click "generate release notes"
   4. Click "publish"
