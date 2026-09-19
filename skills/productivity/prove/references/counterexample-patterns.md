# Counterexample Hunting Patterns

When attempting to falsify requirements in `/prove`, avoid generic or hypothetical edge cases. Ground counterexamples in the concrete constraints, data models, and control flow of the codebase.

Use the following attack vectors to discover unhandled scenarios.

---

## 1. Adjacent Domain States

Systems often handle the primary error or trigger state but omit closely related states that can realistically reach the code path.

* **Pattern**: If the issue handles `FAILED`, examine sibling lifecycle states such as `CANCELLED`, `TIMED_OUT`, `EXPIRED`, `PARTIAL`, or `REJECTED`.
* **Questions**:
  - What happens if the operation is aborted midway and then retried?
  - Does the retry handler assume the previous state was cleanly marked `FAILED`, or can it be called from an intermediate state like `PENDING_RETRY`?

---

## 2. Boundaries & Partitions

Look beyond standard off-by-one errors to semantic boundaries:

* **Quantity Boundaries**:
  - `0`: Empty lists, null bodies, zero-length payloads, zero-amount charges.
  - `1`: Single item, singleton collections, self-referential relations.
  - `N`: Bulk operations, paginated limits, batch boundaries (e.g. exactly at the page boundary of 50 or 100 items).
* **Identity Boundaries**:
  - Self-action: User acting on themselves.
  - Cross-tenant / cross-user: User accessing a resource they don't own.
  - Unauthenticated vs expired session vs active session.
* **Temporal Boundaries**:
  - Timestamp skew or clock drift between services.
  - Exactly expired vs 1 millisecond before expiry.

---

## 3. Persistence Transitions & State Invalidation

Code often passes tests in memory because test fixtures keep state alive, but breaks across persistence or process boundaries.

* **Pattern**: In-memory instance state vs rehydrated database entity.
* **Attack Vectors**:
  - Does the fix work after a full page refresh, service restart, or worker reboot?
  - If cached in Redis/memcached, does updating the underlying entity invalidate the cache?
  - Do transient/computed fields survive serialization and deserialization (JSON, ORM mapping)?
  - Are foreign keys, cascading deletions, or soft-deleted rows handled?

---

## 4. Retries & Idempotency

Requirements often state: "allow retries without duplicate side effects."

* **Attack Vectors**:
  - What happens if the request is retried immediately vs 1 hour later?
  - What if the initial attempt succeeded remotely (e.g. payment charged, email sent) but failed locally before recording the success?
  - Is an idempotency key strictly required, scoped, and checked atomically?
  - Does retrying a failed attempt mutate original creation metadata (timestamps, author IDs, association IDs)?

---

## 5. Concurrency & TOCTOU (Time-of-Check to Time-of-Use)

Whenever code reads a state, validates a condition, and then performs a write, inspect the gap between check and write.

* **Anti-Pattern**:
  ```python
  if not db.find_existing(user_id, item_id):
      db.create_record(user_id, item_id)
  ```
* **Attack Vectors**:
  - Two parallel requests will both pass the `find_existing` check before either inserts.
  - Is there a database uniqueness constraint, advisory lock, or atomic upsert enforcing the rule?
  - Does correctness depend solely on single-threaded execution assumptions that fail under multi-worker environments?

---

## 6. Partial Failures & Rollback Behavior

Operations involving multiple steps or external services often leave inconsistent state when failures happen mid-flight.

* **Attack Vectors**:
  - Step 1 succeeds (DB record created), Step 2 fails (Stripe call throws network error). Does Step 1 get rolled back, or does an orphan record remain?
  - In a batch operation of 10 items, item 7 fails. Does the entire batch fail, or is it partial? If partial, is the status clearly reported?
  - Are distributed transactions or cleanup tasks resilient to crash failures?

---

## 7. Caller Contracts & Downstream Consumers

Never verify only the exact line changed. Trace how existing callers consume the modified behavior.

* **Attack Vectors**:
  - Did changing the return type, nullability, or default value break an unmigrated call site?
  - Does a consumer rely on an undocumented side-effect that was removed or altered?
  - Are events emitted with the exact payload consumers expect?
