import os
import re

filepath = r'c:\Users\ACER\OneDrive\Desktop\Ai_Validator\idea-input.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace addStartupToCollection with just nothing since we don't need it.
# Actually we can just keep deriveStartupName as the backend uses "New Startup Idea" by default if name isn't provided.
# Let's pass the derived name to the backend.

content = re.sub(r"function addStartupToCollection\(idea\) \{[\s\S]*?\}\s*\n", "", content)

# Change fetch('/api/startup') to fetch('/api/startups')
content = content.replace("fetch('/api/startup'", "fetch('/api/startups'")

# Instead of just sending { idea }, send { idea, name: deriveStartupName(idea) }
content = content.replace("body: JSON.stringify({ idea })", "body: JSON.stringify({ idea, name: deriveStartupName(idea) })")

# In the success block, instead of calling addStartupToCollection(result.startup.idea), set the selectedStartupId
# Old: addStartupToCollection(result.startup.idea);
# New: localStorage.setItem('selectedStartupId', result.startup.id);
content = content.replace("addStartupToCollection(result.startup.idea);", "localStorage.setItem('selectedStartupId', result.startup.id);")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content.strip() + "\n")
