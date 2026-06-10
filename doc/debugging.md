# Debugging

## Individual tests

Individual tests are specified in JSON files in the repository,
and their execution can be controlled by editing the JSON file
relevant to a given test.

For example, to enable debugging output on a given test, add
`"debug": true` to a given test file, like below:

```diff
{
+  "debug": true,
  "proposals": [
    "sockets"
  ],
  "operations": [
    {
      "type": "run"
    },
    {
      "type": "wait"
    }
  ]
}
```
