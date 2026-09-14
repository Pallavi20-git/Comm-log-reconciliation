import sqlite3

conn = sqlite3.connect("data/comm_log.db")
cur = conn.cursor()

def run(label, query):
    cur.execute(query)
    result = cur.fetchall()
    print(f"{label}: {result[0][0] if len(result)==1 else result}")

# Step 0: naive count
run("Step 0 - naive count", "SELECT COUNT(*) FROM communication_log")

# Step 1: distinct customers
run("Step 1 - distinct customers", "SELECT COUNT(DISTINCT customer_id) FROM communication_log")

# Step 2: exclude unapproved campaigns
run("Step 2 - exclude unapproved", """
    SELECT COUNT(DISTINCT cl.customer_id)
    FROM communication_log cl
    JOIN campaign c ON c.id = cl.communication_id
    WHERE c.creation_status != 'approval_awaiting'
      AND c.processing_status = 'processed'
""")

# Step 3 / final query
final_query = """
WITH RECURSIVE eligible_campaign AS (
  SELECT * FROM campaign
  WHERE creation_status != 'approval_awaiting'
    AND processing_status = 'processed'
),
root_of AS (
  SELECT id, id AS root_id FROM eligible_campaign WHERE parent_id IS NULL
  UNION ALL
  SELECT ec.id, r.root_id
  FROM eligible_campaign ec
  JOIN root_of r ON ec.parent_id = r.id
),
chain_sizes AS (
  SELECT root_id, COUNT(*) AS n_campaigns FROM root_of GROUP BY root_id
)
SELECT SUM(qualifying_count) AS target_base
FROM (
  SELECT
    CASE WHEN cs.n_campaigns > 1
         THEN COUNT(DISTINCT cl.customer_id)
         ELSE COUNT(*)
    END AS qualifying_count
  FROM root_of r
  JOIN chain_sizes cs ON cs.root_id = r.root_id
  JOIN communication_log cl ON cl.communication_id = r.id
  GROUP BY r.root_id
)
"""
run("Final - target_base", final_query)

# Sanity check breakdown per campaign
print("\nPer-campaign breakdown:")
cur.execute("""
    SELECT communication_id, COUNT(*) AS rows, COUNT(DISTINCT customer_id) AS distinct_customers
    FROM communication_log
    GROUP BY communication_id
""")
for row in cur.fetchall():
    print(row)

conn.close()