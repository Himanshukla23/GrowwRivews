import glob

def update_files():
    files = glob.glob('frontend/src/**/*.tsx', recursive=True)
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if "'http://localhost:8000" in content:
            new_content = content.replace(
                "'http://localhost:8000",
                "`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}"
            ).replace("000/api", "000'}/api").replace("`'", "`")
            
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Updated {f}")

update_files()
