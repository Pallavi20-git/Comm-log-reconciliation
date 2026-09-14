# Comm-Log Reconciliation

## Reconciliation Bridge

| Step | Description | Result | Reason |
|---|---|---|---|
| 0 | Naive count: `SELECT COUNT(*) FROM communication_log` | 30 | Starting point — treats every send attempt as a qualifying send |
| 1 | Switched to `COUNT(DISTINCT customer_id)` across all rows | 25 | Retries create multiple rows for the same customer (e.g. C2 sent under 9001, then again under retry 9002) — a plain row count double-counts them |
| 2 | Excluded campaigns with `creation_status = 'approval_awaiting'` (campaign 9004) | 21 | 9004's messages already sent, but it hasn't cleared approval — unapproved campaigns don't count toward reporting even if the send pipeline already ran |
| 3 | For standalone campaigns (no parent, nothing retries off them — e.g. 9101), stopped deduping by customer; counted every row as its own event | **22** | Customer C20 was legitimately re-targeted twice under standalone campaign 9101 (two different dates, not a retry) — since 9101 isn't a retry chain, both sends are real, separate events |

**Final: 22**

See `query.sql` for the SQL query used to compute this number.