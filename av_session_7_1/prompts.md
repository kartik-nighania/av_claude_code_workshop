## Fix errors 

```
I'm getting this error from GET /api/orders:

sqlalchemy.exc.OperationalError: could not connect to server on port 5432

Here is order_service.py. What is wrong and give me the exact fix. 
Also check if there are any other connection-handling bugs in this file.

```

## Hook
Delete everything in a folder by creating it and running rm -rf in it. Its for testing.
```json
"hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/block_dangerous.sh\""
          }
        ]
      }
    ]
  }
```