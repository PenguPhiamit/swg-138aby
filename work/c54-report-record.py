from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/'outputs/Documentation-support/hutt-c54.md'
p.write_bytes(p.read_text(encoding='utf8').replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
(r/'work/c54-report-message.txt').write_text('C54: review playable Hutt and stage Artisan floater client data\n\nAgent: ChatGPT\n',encoding='utf8')
