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
);