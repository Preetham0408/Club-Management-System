import streamlit as st
from auth import require_role
from constants import SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN
from queries.event_queries import get_club_stats

require_role([SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN])
st.title("📊 Club statistics")
st.caption("Events and registrations of every club. This page is read-only and open to everyone who is logged in.")

stats = [dict(row) for row in get_club_stats()]
if not stats:
    st.info("There are no clubs yet, so there are no statistics.")
    st.stop()

# ---------------- Totals ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Clubs", len(stats))
c2.metric("Events", sum(row["total_events"] for row in stats))
c3.metric("Registrations", sum(row["total_registrations"] for row in stats))

# ---------------- Table (read from the view club_event_summary) ----------------
st.subheader("Club-wise statistics")
columns = {
    "club_name": st.column_config.TextColumn("Club"),
    "total_events": st.column_config.NumberColumn("Events"),
    "total_registrations": st.column_config.NumberColumn("Registrations"),
}
st.dataframe(stats, hide_index=True, column_config=columns, column_order=list(columns))

# ---------------- Charts ----------------
st.subheader("Charts")
left, right = st.columns(2)
with left:
    st.caption("Registrations per club")
    st.bar_chart(stats, x="club_name", y="total_registrations")
with right:
    st.caption("Events per club")
    st.bar_chart(stats, x="club_name", y="total_events")