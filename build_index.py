import pathlib, datetime, os
root = pathlib.Path('.')
out=['# T-34 vs Tiger Library','']

# 1. root-level files
root_files=[f for f in root.iterdir() if f.is_file()]
if root_files:
    out+=['## Root files',
          '| File | Size | Modified |',
          '|------|------|----------|']
    for f in sorted(root_files):
        sz=f.stat().st_size//1024
        dt=datetime.date.fromtimestamp(f.stat().st_mtime)
        out.append(f'| [{f.name}]({f.name}) | {sz} KB | {dt} |')

# 2. every visible sub-folder (recursive)
for folder in sorted(root.iterdir()):
    if folder.is_dir() and not folder.name.startswith('.'):
        out+=['',f'## {folder.name}',
              '| File | Size | Modified |',
              '|------|------|----------|']
        for f in sorted(folder.rglob('*.*')):
            if f.is_file():
                sz=f.stat().st_size//1024
                dt=datetime.date.fromtimestamp(f.stat().st_mtime)
                out.append(f'| [{f.relative_to(root)}]({f.as_posix()}) | {sz} KB | {dt} |')

open('index.md','w',encoding='utf8').write('\n'.join(out))
print('index.md updated')
