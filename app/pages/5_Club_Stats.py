import streamlit as st

from auth import require_role
from constants import (
    SESSION_ROLE_ADMIN,
    SESSION_ROLE_STUDENT,
    SESSION_ROLE_HEAD,
)

from queries.event_queries import get_club_stats


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

require_role([
    SESSION_ROLE_STUDENT,
    SESSION_ROLE_HEAD,
    SESSION_ROLE_ADMIN,
])


# --------------------------------------------------
# CLUB STATISTICS
# --------------------------------------------------

st.title("Club Statistics")

st.write(
    "View event statistics and participation details "
    "for all registered clubs."
)

stats = get_club_stats()


if not stats:
    st.info("No club statistics are available yet.")

else:

    # Convert database rows into dictionaries
    stats_data = [dict(row) for row in stats]

    st.header("Statistics Overview")

    # Total events across all clubs
    total_events = sum(
        row["total_events"] for row in stats_data
    )

    # Total registrations across all clubs
    total_registrations = sum(
        row["total_registrations"] for row in stats_data
    )

    # Number of clubs
    total_clubs = len(stats_data)

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Clubs",
            value=total_clubs,
        )

    with col2:
        st.metric(
            label="Total Events",
            value=total_events,
        )

    with col3:
        st.metric(
            label="Total Registrations",
            value=total_registrations,
        )

    # --------------------------------------------------
    # STATISTICS TABLE
    # --------------------------------------------------

    st.divider()

    st.subheader("Club-wise Statistics")

    st.dataframe(
        stats_data,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # REGISTRATIONS BAR CHART
    # --------------------------------------------------

    st.divider()

    st.subheader("Event Registrations by Club")

    chart_data = {
        row["club_name"]: row["total_registrations"]
        for row in stats_data
    }

    st.bar_chart(chart_data)

    # --------------------------------------------------
    # EVENT COUNT CHART
    # --------------------------------------------------

    st.divider()

    st.subheader("Total Events by Club")

    event_chart_data = {
        row["club_name"]: row["total_events"]
        for row in stats_data
    }

    st.bar_chart(event_chart_data)


# --------------------------------------------------
# READ-ONLY INFORMATION
# --------------------------------------------------

st.divider()

st.info(
    "Club statistics are read-only. "
    "Students, Club Heads, and Administrators "
    "can view these statistics."
)
