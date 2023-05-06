## Expanse: quick access to saved text snippets

```
$ expanse --help
Usage: expanse [OPTIONS] COMMAND [ARGS]...

Options:
  -f, --expansion-file PATH
  --help                     Show this message and exit.

Commands:
  add     Add expansion
  delete  Remove expansion
  dump    Dump expansion file
  edit    Edit expansion
  get     Get expansion contents
  list    List expansions
  show    Show expansion
```

```
$ expanse add -n test -e "Some long text you want to expand to"

$ expanse get test
Some long text you want to expand to
```

