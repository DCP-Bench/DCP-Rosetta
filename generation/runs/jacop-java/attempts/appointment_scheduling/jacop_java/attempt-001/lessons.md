# Lessons: appointment_scheduling

- The brief does not say which index of m is the person and which is the slot. The data notes say m[i][j] = person i free in slot j (the staircase note), so the model reads it that way. The retained model was accepted on all 5 instances, which confirms that reading against the reference.
- Each slot holds at most one person and each person exactly one slot. Both are stated in the description ("into 4 interview slots"), so the model keeps both as posted.
