Blind model. Earlier attempts (20261016-maxicp-java-models) timed out with 30 free face
variables. Variants measured locally on the single instance:
- faces listed in nondecreasing order per die (a die is a multiset, so no set of dice is lost),
  win counts as sum_k below[b][face_a_k] with element: first solution after 168 s;
- registration face-major, descending value order, the "loser wins at most 17" side, and 36
  reified comparisons per relation: all timed out at 120 s;
- adding the implied inequalities face_a[k] > face_b[need_k] (from the sorted faces and the
  19-of-36 threshold, derived in the model's comment): two solutions in 8 s. That is this attempt.
The instance has no fields; the five dice, six faces, 1..12 and the ten relations are fixed by
the statement.
