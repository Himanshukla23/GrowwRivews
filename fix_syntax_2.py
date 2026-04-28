import glob

def fix_syntax_2():
    files = glob.glob('frontend/src/**/*.tsx', recursive=True)
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace the broken string literals
        new_content = content.replace("'),", "`),").replace("')", "` )").replace("` )", "` )").replace("status')", "status`)")
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Fixed {f}")

fix_syntax_2()
