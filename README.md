A simple GitHub Action to add the VBA language annotation to .bas fiels in your repo.

Example worflow:
```yml
name: Add VBA language annotation

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

permissions:
  contents: write

jobs:
  enforce-crlf:
    runs-on: ubuntu-latest
    steps:
    - name: Add VBA language annotation
      uses: DecimalTurn/@main
      with:
        do-checkout: true
        do-push: true
```

Note that in the above example, we are setting `do-checkout` and `do-push` in order to let the action perform those steps for us. If however, you want Enforce-CRLF to be part of a more complex workflow where you've already performed the `git checkout` and/or will perform the `git push` at the end, you can always set those values to false.

```yml
        do-checkout: false
        do-push: false
```