import os

site_dir = 'site'

for root, _, files in os.walk(site_dir):
    for file in files:
        if file.endswith('.html') or file.endswith('.js'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue
                
            new_content = content.replace("?? Hussein's Take", "&#128172; Hussein's Take")
            new_content = new_content.replace("?? HUSSEIN'S TAKE", "&#128172; HUSSEIN'S TAKE")
            new_content = new_content.replace("?? Hussein", "&#128172; Hussein")
            
            # Replace old AI laptop avatars
            new_content = new_content.replace("../images/ai-person-laptop.jpg", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face")
            new_content = new_content.replace("/images/ai-person-laptop.jpg", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face")
            new_content = new_content.replace('src="images/ai-person-laptop.jpg"', 'src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face"')

            # Other broken emojis
            new_content = new_content.replace("Built with ?? for the AI community", "Built with &#10084;&#65039; for the AI community")
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed: {filepath}")
