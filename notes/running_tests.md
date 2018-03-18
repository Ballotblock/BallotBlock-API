# Coverage
Install ``python-coverage`` then execute from
the root project folder:

```python
coverage run -m unittest discover test
coverage html
firefox  htmlcov/index.html
```

``coverage`` will output HTML files that make it
trivial to see which sections of code haven't been
executed yet. These sections should have unittests written
for them!
