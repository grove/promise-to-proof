# Testing Heuristics & Anti-Patterns

When evaluating test evidence during `/prove`, do not equate "tests pass" with "requirement proven." Audit the quality, independence, and sensitivity of each test.

---

## 1. Common Testing Illusions & Anti-Patterns

### Mock Illusion
* **The Flaw**: Mocks configure the mock return value to match the exact requirement, so the test merely verifies that the mock returned what it was told to return.
* **Red Flag**: A test with 15 lines of mock setup and a single assertion verifying that the mock was invoked with arguments configured in line 2.
* **Remedy**: Test across real boundaries or against real in-memory adapters (e.g. SQLite, fake repositories, real serialization).

### Tautological Expectations
* **The Flaw**: The test calculates the expected outcome using the exact same helper, regex, or logic used by the production code.
* **Red Flag**:
  ```ts
  const expected = calculateTax(order); // Same production utility
  expect(res.tax).toEqual(expected);
  ```
* **Remedy**: Hardcode independent oracles derived from the issue or specification:
  ```ts
  // Issue states: $100 order at 8% tax must result in $8.00 tax
  expect(res.tax).toEqual(8.00);
  ```

### Setup Without Assertion
* **The Flaw**: The test executes a complex workflow (e.g. triggers a retry, sends webhooks) but only asserts that the HTTP status is 200 or that no exception was thrown, completely skipping assertions on data integrity, state transitions, or side effects.
* **Remedy**: Explicitly assert the specific business outcome demanded by the issue (e.g. "invoice association preserved", "single charge record exists").

### Non-Sensitive Regression Tests
* **The Flaw**: A test written for a bug that passes even when the bug is present, often because the test fixture does not reproduce the actual conditions of the bug.
* **Remedy**: Perform a **Sensitivity Check** (see below).

### Wrong Level of Observation
* **The Flaw**: Testing private internal variables or intermediate helper calls rather than observable contract behavior at the public seam.
* **Remedy**: Assert on public API responses, database persistence, emitted events, or user-visible side effects.

### Unenforced Assumptions
* **The Flaw**: Code assumes conventions that callers happen to follow today but nothing guarantees (e.g., "ordered events", "non-null foreign keys", "single invocation").
* **Remedy**: Enforce assumptions with type constraints, schema checks, or validation guards—and write tests that verify the violation is prevented.

---

## 2. Executing Sensitivity Checks

A sensitivity check verifies that a regression test is capable of detecting when the requirement is broken.

### When to use:
Apply to 1–3 central regression claims of the issue (especially bug fixes or idempotency guards).

### Protocol:
1. **Identify the core guard or fix**:
   Find the specific lines in the implementation that resolve the issue (e.g., the deduplication query, transaction wrapper, or error fallback).
2. **Introduce a temporary fault**:
   Comment out the guard or invert the condition:
   ```ts
   // TEMPORARY PROVE SENSITIVITY CHECK
   // if (existingRecord) return existingRecord;
   ```
3. **Execute the regression test**:
   The test MUST fail (**turn RED**).
   - If the test still passes, the test is insensitive or tautological. Strengthen the test until it reliably catches the fault.
4. **Restore the implementation**:
   Revert the temporary fault.
5. **Verify GREEN**:
   Confirm the test passes again.
6. **Clean Diff Check**:
   Always verify with `git diff` that no commented code or temporary changes remain before finishing the proof.
