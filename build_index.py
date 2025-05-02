import os, pathlib, datetime
out=['# T-34 vs Tiger Library']
for folder in sorted(pathlib.Path('.').iterdir()):
    if folder.is_dir() and not folder.name.startswith('.'):
        out+=['',f'## {folder.name}','| File | Size | Modified |','|------|------|----------|']
        for f in sorted(folder.rglob('*.*')):
            if f.is_file():
                sz=f.stat().st_size//1024
                dt=datetime.datetime.fromtimestamp(f.stat().st_mtime).date()
                out.append(f'| [{f.relative_to(folder)}]({f.as_posix()}) | {sz} KB | {dt} |')
open('index.md','w',encoding='utf8').write('\n'.join(out))
print('index.md updated')
