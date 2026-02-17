"""Skills page - View and manage agent skills."""

import streamlit as st
from pathlib import Path
import sys

NANOBOT_ROOT = Path(__file__).parent.parent.parent
if str(NANOBOT_ROOT) not in sys.path:
    sys.path.insert(0, str(NANOBOT_ROOT))

st.title(" Skills")
st.markdown("View and manage agent skills - capabilities taught through markdown files")

try:
    from nanobot.config.loader import load_config
    from nanobot.agent.skills import SkillsLoader, BUILTIN_SKILLS_DIR
    
    config = load_config()
    workspace = config.workspace_path
    skills_loader = SkillsLoader(workspace)
    
    tab1, tab2, tab3 = st.tabs(["Available Skills", "Create Skill", "About Skills"])
    
    with tab1:
        st.subheader("All Available Skills")
        
        all_skills = skills_loader.list_skills(filter_unavailable=False)
        
        if all_skills:
            for skill in all_skills:
                meta = skills_loader.get_skill_metadata(skill["name"])
                skill_meta = skills_loader._get_skill_meta(skill["name"])
                available = skills_loader._check_requirements(skill_meta)
                
                icon = "" if available else "N"
                source_icon = "" if skill["source"] == "builtin" else ""
                
                with st.expander(f"{icon} {source_icon} {skill['name']}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Source", skill["source"])
                    
                    with col2:
                        st.metric("Available", "Yes" if available else "No")
                    
                    with col3:
                        if meta:
                            always = meta.get("always", False) or skill_meta.get("always", False)
                            st.metric("Always Load", "Yes" if always else "No")
                    
                    if meta and meta.get("description"):
                        st.markdown(f"**Description:** {meta['description']}")
                    
                    missing = skills_loader._get_missing_requirements(skill_meta)
                    if missing:
                        st.warning(f"Missing requirements: {missing}")
                    
                    st.markdown(f"**Location:** `{skill['path']}`")
                    
                    content = skills_loader.load_skill(skill["name"])
                    if content:
                        with st.expander("View SKILL.md"):
                            st.markdown(content)
            
            st.markdown("---")
            
            st.subheader("Skills Summary")
            
            skills_data = []
            for skill in all_skills:
                meta = skills_loader.get_skill_metadata(skill["name"])
                skill_meta = skills_loader._get_skill_meta(skill["name"])
                available = skills_loader._check_requirements(skill_meta)
                
                skills_data.append({
                    "Name": skill["name"],
                    "Source": skill["source"],
                    "Available": "" if available else "N",
                    "Description": (meta or {}).get("description", "")[:50] if meta else ""
                })
            
            st.dataframe(skills_data, use_container_width=True, hide_index=True)
        else:
            st.info("No skills found.")
        
        st.markdown("---")
        
        always_skills = skills_loader.get_always_skills()
        if always_skills:
            st.subheader("Always-Loaded Skills")
            st.markdown("These skills are always included in the agent's context:")
            for name in always_skills:
                st.markdown(f"- {name}")
    
    with tab2:
        st.subheader("Create New Skill")
        st.markdown("Create a custom skill in your workspace skills directory.")
        
        skill_name = st.text_input("Skill Name", placeholder="my-custom-skill", help="Use lowercase and hyphens")
        skill_description = st.text_input("Description", placeholder="What this skill does")
        always_load = st.checkbox("Always Load", help="If checked, this skill will always be loaded into agent context")
        
        skill_content = st.text_area(
            "Skill Content (Markdown)",
            value="""# Skill Name

Describe what this skill teaches the agent to do.

## Instructions

Step-by-step instructions for the agent.

## Examples

Example usage patterns.

## Notes

Additional context or tips.
""",
            height=300
        )
        
        if st.button("Create Skill", type="primary"):
            if not skill_name:
                st.error("Skill name is required")
            else:
                skill_dir = workspace / "skills" / skill_name
                skill_file = skill_dir / "SKILL.md"
                
                if skill_file.exists():
                    st.error(f"Skill '{skill_name}' already exists")
                else:
                    frontmatter = "---\n"
                    if skill_description:
                        frontmatter += f'description: "{skill_description}"\n'
                    if always_load:
                        frontmatter += "always: true\n"
                    frontmatter += "---\n\n"
                    
                    skill_dir.mkdir(parents=True, exist_ok=True)
                    skill_file.write_text(frontmatter + skill_content)
                    
                    st.success(f"Skill '{skill_name}' created at {skill_file}")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("""
        **Skill Structure:**
        ```
        workspace/skills/
        └── skill-name/
            └── SKILL.md    # Markdown file with YAML frontmatter
        ```
        
        **Frontmatter Fields:**
        - `description`: Brief description of the skill
        - `always`: If true, always loaded into context
        - `metadata`: JSON for nanobot-specific settings
        """)
    
    with tab3:
        st.subheader("About Skills")
        
        st.markdown("""
        **What are Skills?**
        
        Skills are markdown files (SKILL.md) that teach the agent how to use 
        specific tools or perform certain tasks. They extend the agent's 
        capabilities through natural language instructions.
        
        **How Skills Work:**
        
        1. Skills are discovered from two locations:
           - **Built-in skills**: `nanobot/skills/` directory
           - **Workspace skills**: `~/.nanobot/workspace/skills/` directory
        
        2. Skills have optional YAML frontmatter:
           ```yaml
           ---
           description: "Weather information"
           always: false
           metadata: {"nanobot": {"requires": {"bins": ["curl"]}}}
           ---
           ```
        
        3. "Always" skills are loaded into every conversation context
        
        4. Other skills are listed in a summary, and the agent reads them on-demand
        
        **Built-in Skills:**
        """)
        
        if BUILTIN_SKILLS_DIR.exists():
            builtin_skills = list(BUILTIN_SKILLS_DIR.iterdir())
            for skill_dir in builtin_skills:
                if skill_dir.is_dir():
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        st.markdown(f"- **{skill_dir.name}**: `{skill_file}`")
        
        st.markdown("""
        ---
        
        **Skill Requirements:**
        
        Skills can specify requirements (bins, env vars) that must be met:
        ```yaml
        metadata:
          nanobot:
            requires:
              bins: ["gh", "git"]
              env: ["GITHUB_TOKEN"]
        ```
        
        Skills with unmet requirements are marked as unavailable.
        """)

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure nanobot is properly installed and configured.")