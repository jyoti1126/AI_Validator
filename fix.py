import os
files = ['dashboard.html', 'overview.html', 'market.html', 'competition.html', 'risks.html', 'business.html', 'mvp.html', 'experiments.html', 'startups.html']
for f in files:
    path = os.path.join(r'c:\Users\ACER\OneDrive\Desktop\Ai_Validator', f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('<script src="shared.js"></script>`n  <script src="', '<script src="shared.js"></script>\n  <script src="')
    if f == 'startups.html' and 'shared.js' not in content:
        content = content.replace('<script src="startups.js"></script>', '<script src="shared.js"></script>\n  <script src="startups.js"></script>')
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
