# Acceptance contract: Sum
Contract revision: v1
Parent: None
Source: The request is to preserve ordinary integer addition.

| ID | Requirement | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|
| R1 | sum([2, 3]) returns 5 | Python sum | Literal 5 | python3 -c "assert sum([2, 3]) == 5" | planned |
