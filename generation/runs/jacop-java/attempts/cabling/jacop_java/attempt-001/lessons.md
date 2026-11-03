# Lessons: cabling, attempt-001

- The brief lists cable_struct as unbindable (mixed str and int per row). The jacop_java runner
  passes the JSON through unchanged, so the model reads each row with getString/getInt. This worked
  on all 5 instances, so the unbindable flag did not block this integration.
- Repeated-cable weights are written as repeated distance variables in a SumInt, which avoids a
  weighted-sum API. The same length variable is listed k times for k cables.
