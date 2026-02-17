"""Cron page - Manage scheduled tasks."""

import streamlit as st
from pathlib import Path
import sys
import asyncio
from datetime import datetime

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title("Cron Jobs")
st.markdown("Schedule and manage automated tasks for your AI assistant")

try:
    from nanobot.config.loader import get_data_dir
    from nanobot.cron.service import CronService
    from nanobot.cron.types import CronSchedule
    
    cron_store_path = get_data_dir() / "cron" / "jobs.json"
    cron = CronService(cron_store_path)
    
    tab1, tab2 = st.tabs(["Jobs List", "Add Job"])
    
    with tab1:
        jobs = cron.list_jobs(include_disabled=True)
        
        if jobs:
            for job in jobs:
                with st.expander(f"{'' if job.enabled else 'N'} {job.name} (`{job.id}`)"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if job.schedule.kind == "every":
                            every_s = (job.schedule.every_ms or 0) // 1000
                            st.metric("Schedule", f"Every {every_s}s")
                        elif job.schedule.kind == "cron":
                            st.metric("Cron", job.schedule.expr or "N/A")
                        else:
                            st.metric("Schedule", "One-time")
                    
                    with col2:
                        if job.state.next_run_at_ms:
                            ts = job.state.next_run_at_ms / 1000
                            next_run = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                            st.metric("Next Run", next_run)
                        else:
                            st.metric("Next Run", "N/A")
                    
                    with col3:
                        status = " Enabled" if job.enabled else "N Disabled"
                        if job.state.last_status:
                            status += f" | Last: {job.state.last_status}"
                        st.metric("Status", status)
                    
                    st.markdown(f"**Message:** `{job.payload.message[:100]}...`" if len(job.payload.message) > 100 else f"**Message:** `{job.payload.message}`")
                    
                    if job.payload.deliver:
                        st.info(f"Delivers to: {job.payload.channel}:{job.payload.to}")
                    
                    if job.state.last_error:
                        st.error(f"Last Error: {job.state.last_error}")
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        if st.button("Run Now", key=f"run_{job.id}"):
                            async def run_job():
                                return await cron.run_job(job.id, force=True)
                            
                            result = asyncio.run(run_job())
                            if result:
                                st.success("Job executed!")
                            else:
                                st.error("Failed to execute job")
                            st.rerun()
                    
                    with col_b:
                        if job.enabled:
                            if st.button("Disable", key=f"disable_{job.id}"):
                                cron.enable_job(job.id, enabled=False)
                                st.success("Job disabled")
                                st.rerun()
                        else:
                            if st.button("Enable", key=f"enable_{job.id}"):
                                cron.enable_job(job.id, enabled=True)
                                st.success("Job enabled")
                                st.rerun()
                    
                    with col_c:
                        if st.button("Delete", key=f"delete_{job.id}"):
                            cron.remove_job(job.id)
                            st.success("Job deleted")
                            st.rerun()
                    
                    with col_d:
                        created = datetime.fromtimestamp(job.created_at_ms / 1000).strftime("%Y-%m-%d")
                        st.caption(f"Created: {created}")
            
            st.markdown("---")
            st.subheader("Jobs Summary")
            
            jobs_data = []
            for job in jobs:
                if job.schedule.kind == "every":
                    sched = f"Every {(job.schedule.every_ms or 0) // 1000}s"
                elif job.schedule.kind == "cron":
                    sched = f"Cron: {job.schedule.expr}"
                else:
                    sched = "One-time"
                
                next_run = ""
                if job.state.next_run_at_ms:
                    ts = job.state.next_run_at_ms / 1000
                    next_run = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
                
                jobs_data.append({
                    "ID": job.id,
                    "Name": job.name,
                    "Schedule": sched,
                    "Enabled": "" if job.enabled else "N",
                    "Next Run": next_run
                })
            
            st.dataframe(jobs_data, use_container_width=True, hide_index=True)
        else:
            st.info("No scheduled jobs. Use the 'Add Job' tab to create one.")
    
    with tab2:
        st.subheader("Create New Scheduled Job")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Job Name", placeholder="Daily reminder")
            message = st.text_area(
                "Message for Agent",
                placeholder="Tell me about my daily standup meeting at 9 AM",
                height=100,
                help="This message will be sent to the agent when the job runs"
            )
        
        with col2:
            schedule_type = st.selectbox(
                "Schedule Type",
                ["Interval (every N seconds)", "Cron Expression", "One-time (at specific time)"]
            )
            
            if schedule_type == "Interval (every N seconds)":
                every_seconds = st.number_input("Run every (seconds)", min_value=1, value=3600)
                tz = None
                cron_expr = None
                at_time = None
            elif schedule_type == "Cron Expression":
                cron_expr = st.text_input("Cron Expression", placeholder="0 9 * * *")
                st.caption("Format: minute hour day month weekday (e.g., `0 9 * * *` = daily at 9:00)")
                tz = st.text_input("Timezone (optional)", placeholder="America/Vancouver")
                every_seconds = None
                at_time = None
            else:
                at_time = st.text_input("Run at (ISO datetime)", placeholder="2024-12-25T09:00:00")
                every_seconds = None
                cron_expr = None
                tz = None
        
        st.markdown("---")
        st.subheader("Delivery Options")
        
        deliver = st.checkbox("Deliver response to channel", help="Send the agent's response to a specific channel")
        
        channel = None
        to = None
        
        if deliver:
            col_ch, col_to = st.columns(2)
            with col_ch:
                channel = st.selectbox(
                    "Channel",
                    ["telegram", "whatsapp", "discord", "slack", "feishu", "email", "mochat", "dingtalk", "qq"]
                )
            with col_to:
                to = st.text_input("Recipient", placeholder="user_id or chat_id")
        
        if st.button("Create Job", type="primary"):
            if not name or not message:
                st.error("Name and message are required")
            else:
                try:
                    if schedule_type == "Interval (every N seconds)":
                        schedule = CronSchedule(kind="every", every_ms=every_seconds * 1000)
                    elif schedule_type == "Cron Expression":
                        schedule = CronSchedule(kind="cron", expr=cron_expr, tz=tz)
                    else:
                        from datetime import datetime as dt
                        at_dt = dt.fromisoformat(at_time)
                        schedule = CronSchedule(kind="at", at_ms=int(at_dt.timestamp() * 1000))
                    
                    job = cron.add_job(
                        name=name,
                        schedule=schedule,
                        message=message,
                        deliver=deliver,
                        channel=channel,
                        to=to
                    )
                    
                    st.success(f"Job '{job.name}' created with ID: {job.id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating job: {e}")
    
    st.markdown("---")
    st.markdown("""
    **Schedule Types:**
    - **Interval**: Run every N seconds (e.g., every 3600 seconds = every hour)
    - **Cron Expression**: Standard cron format (e.g., `0 9 * * *` = daily at 9:00)
    - **One-time**: Run once at a specific datetime (ISO format)
    
    **Delivery:**
    - When enabled, the agent's response will be sent to the specified channel/recipient
    - Useful for reminders, notifications, and scheduled reports
    """)
    
except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed and configured.")