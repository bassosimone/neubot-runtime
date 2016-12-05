Welcome to Neubot Run **v0.5.0** documentation!

# How to generate documentation

We use [mkdocs](http://www.mkdocs.org/) to generate HTML documentation
from markdown files. To regenerate documentation, you need to have a
recent version of Python installed. Specifically, the following commands
shows how you can generate the HTML files from the markdown. You must
run them from the toplevel directory (i.e. the one that contains the
`AUTHORS` file):

```
virtualenv __venv__
source __venv__/bin/activate
pip install mkdocs
mkdocs build
```
