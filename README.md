A simple GitHub Action to add the BASIC language annotation (`'@Lang <Language>`) to .bas files in your repo.

Example worflow:
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
  run:
    runs-on: ubuntu-latest
    steps:
    - name: Add BASIC language annotation
      uses: DecimalTurn/BASIC-Language-Annotation@8779a917eb1e837318a15f895d5eede48dcb9c24 #v1.0.0
      with:
        do-checkout: true
        do-push: true
```

Note that in the above example, we are setting `do-checkout` and `do-push` in order to let the action perform those steps for us. If however, you want this action to be part of a more complex workflow where you've already performed the `git checkout` and/or will perform the `git push` at the end, you can always set those values to false.

```yml
        do-checkout: false
        do-push: false
```
