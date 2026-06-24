with open('orchestrator/v32_dopamine_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 169-178 (0-based indices 168-177) which are the duplicate block
# Line 168 (index 167) is already the correct '}}}"""' close
# Lines 169-178 (indices 168-177) are the stale duplicate — delete them
del lines[168:178]

with open('orchestrator/v32_dopamine_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Validate
import ast
with open('orchestrator/v32_dopamine_engine.py', 'r', encoding='utf-8') as f:
    source = f.read()
try:
    ast.parse(source)
    print('SYNTAX OK - File is clean and valid Python!')
except SyntaxError as e:
    print(f'SYNTAX ERROR at line {e.lineno}: {e.msg}')
