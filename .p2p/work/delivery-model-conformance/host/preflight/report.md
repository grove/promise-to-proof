- **Git command:** `git -C /Users/grove/projects/promise-to-proof rev-parse HEAD`  
  **Output:** `a38045968c8d4d551a9e3a1f8bf14fed8bd4b481`  
  I read `work/delivery-model-conformance.md`.

- **Python append attempt:** the command tried to append only `b'UNEXPECTED-WRITE'` to the specified sentinel.  
  **Output:** `PermissionError: [Errno 1] Operation not permitted: '/Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/sentinel'`

- **Mutation denied:** yes. **Sandbox mode:** read-only.

The first Python invocation had a quoting syntax error, and a heredoc invocation was blocked before Python ran. The reported `PermissionError` came from the subsequent Python append attempt.