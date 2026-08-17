import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
result = payload.get('result', {})
print('title=', result.get('title'))
for resource in result.get('resources', []):
    print(resource.get('name'), resource.get('format'), resource.get('url'))
