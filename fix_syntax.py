import glob

def fix_syntax():
    files = glob.glob('frontend/src/**/*.tsx', recursive=True)
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace the broken string literals
        # fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/status');
        # fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/generate-report', {
        new_content = content.replace("');", "`);").replace("', {", "`, {")
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Fixed {f}")

fix_syntax()
