import streamlit as st
import sqlite3 as sql
import uuid
from datetime import datetime, timezone

st.title('Every day - Goal Tracker')

def connect(db_file=""):
    conn = None
    try:
        conn = sql.connect(db_file)
    except Exception as ex:
        st.exception(ex)
    return conn

def create_schema(conn):
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tracks(
            track_id varchar,
            title varchar,
            deleted bool
        );
                    """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tracking(
            track_id varchar,
            date datetime
        );
                    """)
        conn.commit();
    except Exception as ex:
        st.exception(ex)

def settings():
    st.header("Settings and management")

    conn = connect(db_file="goals.db")
    create_schema(conn)

    with st.form("create_track"):
        st.write("Create track")
        title = st.text_input("Title")
        submitted = st.form_submit_button("create")
        if submitted:
            try:
                track_id = str(uuid.uuid4())
                conn.execute("INSERT INTO tracks (track_id,title,deleted) VALUES (?,?,?)",(track_id,title,False))
                conn.commit();
                st.success("Track created")
            except Exception as ex:
                st.exception(ex)

    tracks = []
    try:
        query = conn.execute("SELECT track_id,title FROM tracks WHERE deleted = false")
        tracks = query.fetchall();
    except Exception as ex:
        st.exception(ex)

    with st.form("delete_track"):
        st.write("Delete track")
        track = st.selectbox(label="Select a track",options=tracks,format_func=lambda opt: opt[1])
        submitted = st.form_submit_button("delete")
        if submitted:
            try:
                conn.execute("UPDATE tracks SET deleted = ? WHERE track_id = ?",(True,track[0]))
                conn.commit();
                st.success("Track deleted")
            except Exception as ex:
                st.exception(ex)

def track():
    st.header("Register activicty")

    conn = connect(db_file="goals.db")
    create_schema(conn)

    tracks = []
    try:
        query = conn.execute("SELECT track_id,title FROM tracks WHERE deleted = false")
        tracks = query.fetchall();
    except Exception as ex:
        st.exception(ex)

    with st.form("track"):
        track = st.selectbox(label="Select a track",options=tracks,format_func=lambda opt: opt[1])
        date = st.date_input("When")
        submitted = st.form_submit_button("track")
        if submitted:
            try:
                conn.execute("INSERT INTO tracking (track_id,date) VALUES (?,?)",(track[0],date))
                conn.commit();
                st.success("Tracked")
            except Exception as ex:
                st.exception(ex)

def latest():
    st.header("Latest activicty")

    conn = connect(db_file="goals.db")
    create_schema(conn)

    tracking = []
    try:
        query = conn.execute("""
        SELECT 
            tracks.track_id as track_id,
            tracks.title as title,
            strftime('%Y-%m-%d',tracking.date) as day
        FROM tracking
        INNER JOIN
            tracks ON tracks.track_id=tracking.track_id
        WHERE
            tracking.date >= date('now','-7 day')
            AND
            tracks.deleted = false
        GROUP BY
            strftime('%Y-%m-%d',tracking.date), tracking.track_id
        ORDER BY
            title, day
        """)
        tracking = query.fetchall();
    except Exception as ex:
        st.exception(ex)

    data = {}
    today = datetime.now()

    for track in tracking:
        if track[1] not in data:
            data[track[1]] = [False] * 7
        track_date = datetime.strptime(track[2],'%Y-%m-%d')
        delta = today - track_date;
        data[track[1]][6 - delta.days] = True

    col1, col2 = st.columns([1,5])

    for key in data:
        col1.write(key)
        line = ""
        for check in data[key]:
            if check:
                line += ":large_green_circle:"
            else:
                line += ":white_circle:"
            line += "   "
        col2.write(line)

with st.expander("Settings",expanded=False):
    settings()

with st.expander("Track",expanded=True):
    track()

with st.expander("Activity",expanded=True):
    latest()

