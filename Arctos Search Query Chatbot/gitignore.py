#!/usr/bin/env python
# coding: utf-8

# In[1]:


with open(".gitignore", "w") as f:
    f.write("""
__pycache__/
*.py[cod]
*.egg-info/
.env
.DS_Store
.vscode/
.idea/
.streamlit/secrets.toml
*.ipynb
venv/
env/
""")


# In[ ]:




