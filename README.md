A simple GitHub Action to add the BASIC language annotation (`'@Lang <Language>`) to .bas files in your repo.

Example worflow:

`Path: /.github/workflows/add-language-annotation.yml`
```yml
name: Add BASIC language annotation

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

permissions:
  contents: write

jobs:
  add-language-annotation:
    runs-on: ubuntu-latest
    steps:
    - name: Add BASIC language annotation
      uses: DecimalTurn/BASIC-Language-Annotation@ecd0ad8ee06bf18822668504b5422b7c51299ba1 #v2.0.0
      with:
        language: VBA
        do-checkout: true
        do-push: true
```

Note that in the above example, we are setting `do-checkout` and `do-push` in order to let the action perform those steps for us. If however, you want this action to be part of a more complex workflow where you've already performed the `git checkout` and/or will perform the `git push` at the end, you can always set those values to false.

```yml
        do-checkout: false
        do-push: false
```
