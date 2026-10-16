"""Read only two fixed public source files at the gate's recorded commit."""
import hashlib
import json
import subprocess

root = '/opt/swg/Core3-dev'
pin = '80895f63'
paths = ['MMOCoreORB/src/server/zone/packets/object/DataTransform.h',
         'MMOCoreORB/src/server/zone/objects/creature/commands/HealEnhanceCommand.h']
for path in paths:
    raw = subprocess.check_output(['git', '-C', root, 'show', pin+':'+path])
    text = raw.decode('utf-8')
    print(json.dumps({'pin': pin, 'file': path, 'sha256': hashlib.sha256(raw).hexdigest()}))
    for i, line in enumerate(text.splitlines(), 1):
        if any(x in line for x in ['/*', '*/', 'checkMovementCollision', '!DT-checkCollision',
                                    '!posture', '!DT_checkSpeedHackTests_POS', 're-apply', 'buffPower < currentBuff']):
            print(f'{i}: {line}')
