from pathlib import Path
from datetime import datetime,timezone,timedelta
import html,json,re,textwrap
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,Table,TableStyle,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'outputs'
TARGET=OUT/'SWG-Complete-Project-Record.pdf'
TEMP=BASE/'tmp/pdfs';TEMP.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Segoe','C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('SegoeBold','C:/Windows/Fonts/segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('Consolas','C:/Windows/Fonts/consola.ttf'))
pdfmetrics.registerFontFamily('Segoe',normal='Segoe',bold='SegoeBold',italic='Segoe',boldItalic='SegoeBold')
INK=colors.HexColor('#172D46');ACCENT=colors.HexColor('#C9792D');MUTED=colors.HexColor('#596B7E');PALE=colors.HexColor('#F0F4F7')
PAGE_W,PAGE_H=A4
WIDTH=PAGE_W-96
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body',fontName='Segoe',fontSize=9.3,leading=13.6,textColor=INK,spaceAfter=7,splitLongWords=True))
styles.add(ParagraphStyle(name='BookH1',fontName='SegoeBold',fontSize=18,leading=22,textColor=INK,spaceBefore=15,spaceAfter=10,keepWithNext=True))
styles.add(ParagraphStyle(name='BookH2',fontName='SegoeBold',fontSize=12.2,leading=16,textColor=INK,spaceBefore=10,spaceAfter=6,keepWithNext=True))
styles.add(ParagraphStyle(name='BookH3',fontName='SegoeBold',fontSize=10,leading=13,textColor=INK,spaceBefore=8,spaceAfter=5,keepWithNext=True))
styles.add(ParagraphStyle(name='Small',fontName='Segoe',fontSize=8,leading=11,textColor=MUTED,spaceAfter=6,splitLongWords=True))
styles.add(ParagraphStyle(name='Mono',fontName='Consolas',fontSize=7.6,leading=10,textColor=INK,backColor=PALE,borderPadding=7,spaceAfter=8,wordWrap='CJK'))
styles.add(ParagraphStyle(name='Cell',fontName='Segoe',fontSize=8,leading=10.8,textColor=INK,wordWrap='CJK'))
styles.add(ParagraphStyle(name='CellHead',fontName='SegoeBold',fontSize=8,leading=10.8,textColor=colors.white,wordWrap='CJK'))
styles.add(ParagraphStyle(name='Quote',parent=styles['Body'],leftIndent=12,borderColor=ACCENT,borderWidth=1,borderPadding=7,backColor=PALE))

def normalize(text):
    for a,b in {'\u2010':'-','\u2011':'-','\u2012':'-','\u2013':'-','\u2014':' - ','\u2212':'-','\u2018':"'",'\u2019':"'",'\u201c':'"','\u201d':'"','\u00a0':' ','\u2026':'...','\u2192':' -> ','\u2190':' <- ','\u00d7':'x'}.items():text=text.replace(a,b)
    return ''.join(c for c in text if ord(c)<0x1F000)

def inline(text):
    text=normalize(text)
    links=[]
    def link(m):
        label,url=m.group(1),m.group(2).strip('<>')
        if url.startswith(('http://','https://')):
            value='<a href="'+html.escape(url,quote=True)+'" color="#245D82">'+html.escape(label)+'</a>'
        else:value=html.escape(label)
        links.append(value);return '@@LINK'+str(len(links)-1)+'@@'
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,text)
    text=html.escape(text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'`([^`]+)`',r'<font name="Consolas">\1</font>',text)
    for i,val in enumerate(links):text=text.replace('@@LINK'+str(i)+'@@',val)
    return text

def p(text,style='Body'):
    return Paragraph(inline(str(text)),styles[style])

class Book(BaseDocTemplate):
    def __init__(self,path,**kwargs):
        super().__init__(str(path),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=55,bottomMargin=45,title='Local SWG Galaxy - Complete Project Record',author='Project record prepared with Codex',**kwargs)
        frame=Frame(48,45,WIDTH,PAGE_H-100,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='standard',frames=[frame],onPage=self.page))
        self.heading_counter=0
    def page(self,canvas,doc):
        canvas.saveState()
        if doc.page>1:
            canvas.setFont('SegoeBold',8);canvas.setFillColor(MUTED)
            canvas.drawString(48,PAGE_H-30,'LOCAL SWG GALAXY / PROJECT RECORD')
            canvas.setStrokeColor(colors.HexColor('#D9E1E8'));canvas.line(48,PAGE_H-39,PAGE_W-48,PAGE_H-39)
        canvas.setFont('Segoe',7.5);canvas.setFillColor(MUTED)
        canvas.drawString(48,25,'October 13, 2026  |  Pre-CU sandbox  |  Private credentials omitted')
        canvas.drawRightString(PAGE_W-48,25,str(doc.page))
        canvas.restoreState()
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and flowable.style.name in ('BookH1','BookH2'):
            level=0 if flowable.style.name=='BookH1' else 1
            title=flowable.getPlainText()
            if title=='Contents':return
            key='section-'+str(self.seq.nextf('heading'))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title,key,level=level,closed=False)
            self.notify('TOCEntry',(level,title,self.page,key))

story=[]
def heading(title,level=1):story.append(p(title,'BookH'+str(level)))
def para(text,style='Body'):story.append(p(text,style))
def table(headers,rows,widths=None):
    n=len(headers)
    widths=widths or ([WIDTH*.32,WIDTH*.68] if n==2 else [WIDTH/n]*n)
    cells=[[p(x,'CellHead') for x in headers]]+[[p(str(x),'Cell') for x in row] for row in rows]
    obj=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    obj.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),('LINEBELOW',(0,0),(-1,0),1,ACCENT),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#D9E1E8'))]))
    story.extend([obj,Spacer(1,9)])

def markdown(text,demote=False,skip_title=True):
    lines=normalize(text).splitlines();i=0;buffer=[]
    def flush():
        if buffer:para(' '.join(buffer));buffer.clear()
    while i<len(lines):
        line=lines[i].rstrip();i+=1
        if not line.strip():flush();continue
        if line.startswith('```'):
            flush();code=[]
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            i+=1
            formatted=[]
            for c in code:formatted.extend(textwrap.wrap(c,width=92,replace_whitespace=False,drop_whitespace=False) or [' '])
            story.append(Paragraph('<br/>'.join(html.escape(c) for c in formatted),styles['Mono']));continue
        if line.startswith('|') and i<len(lines) and re.match(r'^\|?[\s:|\-]+$',lines[i]):
            flush();headers=[x.strip() for x in line.strip('|').split('|')];i+=1;rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[x.strip() for x in lines[i].strip('|').split('|')]
                if len(cells)==len(headers):rows.append(cells)
                i+=1
            table(headers,rows);continue
        if line.startswith('#'):
            flush();level=len(line)-len(line.lstrip('#'));title=line[level:].strip()
            if level==1 and skip_title:continue
            level=min(3,max(1,level-1)+(1 if demote else 0))
            heading(title,level);continue
        match=re.match(r'^\s*(?:[-*]|(\d+)\.)\s+(.+)$',line)
        if match:
            flush();prefix=match[1]+'. ' if match[1] else '- '
            para(prefix+match[2]);continue
        buffer.append(line.strip())
    flush()

# Cover.
story.append(Spacer(1,72))
story.append(Paragraph('LOCAL GALAXY',ParagraphStyle('CoverEyebrow',fontName='SegoeBold',fontSize=11,textColor=ACCENT,tracking=1.6,spaceAfter=15)))
story.append(Paragraph('Star Wars Galaxies',ParagraphStyle('CoverTitle',fontName='SegoeBold',fontSize=34,leading=40,textColor=INK,spaceAfter=11)))
story.append(Paragraph('Complete project record',ParagraphStyle('CoverSub',fontName='Segoe',fontSize=23,leading=29,textColor=INK,spaceAfter=25)))
para('Setup, troubleshooting, developer baseline, sandbox changes, community content and recovery.','Quote')
story.append(Spacer(1,22))
para('Prepared October 13, 2026<br/>America/Los_Angeles'.replace('<br/>',' - '),'Small')
validation=json.loads((OUT/'SWG-sandbox-validation.json').read_text(encoding='utf-8'))
install=json.loads((OUT/'SWG-community-install.json').read_text(encoding='utf-8'))
settings=json.loads((OUT/'SWG-sandbox-settings.json').read_text(encoding='utf-8'))
collection=json.loads((OUT/'Community-content/collection-manifest.json').read_text(encoding='utf-8'))
assets=json.loads((OUT/'Community-content/MTG-assets/manifest.json').read_text(encoding='utf-8'))
if not validation.get('all_23_installed_assets_match_download'):raise RuntimeError('Final asset verification required before PDF export.')
table(['Current milestone','Verified state'],[['Galaxy','Rebuilt, initialized and listening on the game ports'],['Community library',str(install['inventory_catalog_entries'])+' item/schematic catalog entries; 23 matching asset archives'],['Validation','Lua syntax and startup passed; gameplay tests remain'],['Recovery','Verified clean pre-sandbox snapshot retained']])
para('This document contains no account password, database password or database secret. The original chat and local evidence files remain available.','Small')
story.append(PageBreak())
heading('Contents')
toc=TableOfContents()
toc.levelStyles=[ParagraphStyle('TOC0',fontName='Segoe',fontSize=9.5,leading=14,leftIndent=0,firstLineIndent=0,spaceBefore=5,textColor=INK),ParagraphStyle('TOC1',fontName='Segoe',fontSize=8,leading=11,leftIndent=14,firstLineIndent=0,spaceBefore=2,textColor=MUTED)]
story.append(toc);story.append(PageBreak())
heading('Current state at export')
table(['Check','Result'],[['Core3 base revision','403893d9b9f8e6fa712fbb3cb1fcd8f0fe45bb79; local changes are captured separately'],['Engine revision','4cbf39336e0e727dfef861fbe65bd303ce70fd37'],['Startup',str(validation['server_initialized'])+'; '+validation['startup_since']],['Game ports',str(validation['expected_game_ports_listening'])+' (UDP 44453, 44462, 44463)'],['Database','Schema '+validation['schema']+'; account/character counts '+validation['account_and_character_counts'].replace('\n',' / ')],['Owner level',validation['owner_admin_level']],['Error scan',str(len(validation['error_lines']))+' error/fatal/Lua error lines in the captured startup'],['Warnings',str(validation.get('warning_line_count','unknown'))+' lines; '+str(len(validation.get('referenced_warning_paths',[])))+' extracted referenced paths'],['Asset copies','All 23 server and client copies match their downloaded SHA-256 hashes'],['Client action','Reopen the client to load the new assets and preferences']])
para('Startup and syntax checks establish a working development server. They do not establish complete behavior for every catalog item, quest, house or ship. Warnings remain visible and are recorded below.','Quote')
markdown((OUT/'SWG-project-record.md').read_text(encoding='utf-8'))

story.append(PageBreak());heading('Exact sandbox settings')
table(['Setting','Applied value'],[[k.replace('_',' ').title(),json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict,bool)) else str(v)] for k,v in settings['profile'].items()])
heading('Changed profile files',2)
for name in settings['changed_files']:para(name,'Small')
para('Additional content loaders, the generated MTG builder catalog, adapted quest and client archive priorities are captured in the local source package and installation record.','Small')

story.append(PageBreak());heading('Community collection and installed assets')
table(['Component','Count / state'],[['MTG published files',collection['mtg_published_files']],['SR reference Lua files',collection['sr_reference_lua_files']],['SR files excluded by notice',len(collection['sr_excluded_notice_files'])],['Installed asset archives',install['asset_archives_installed']],['Lua files syntax checked',install['lua_files_syntax_checked']],['Builder item/schematic entries',install['inventory_catalog_entries']],['Additional ground planets','Assets collected; destinations not enabled']])
table(['Archive','MiB','SHA-256 (download and installed copies)'],[[x['name'],f"{x['bytes']/1024/1024:.1f}",x['sha256']] for x in assets['files']],[WIDTH*.36,WIDTH*.1,WIDTH*.54])
heading('Source bundle checksums',2)
table(['Bundle','SHA-256'],[[name,value['sha256']] for name,value in collection['archives'].items()])
heading('Attribution and unavailable material',2)
for block in (OUT/'Community-content/CREDITS-and-sources.txt').read_text(encoding='utf-8').split('\n\n'):
    if block.strip():para(' '.join(block.splitlines()),'Small')

story.append(PageBreak());heading('Current warning inventory')
para('The captured startup contains '+str(validation.get('warning_line_count'))+' warning lines. Many are repeated template-form/inheritance warnings. This list contains paths extracted by the documented missing-reference patterns; it is not a proof that all other templates are correct.','Small')
for path in validation.get('referenced_warning_paths',[]):para(path,'Mono')
heading('Live gameplay acceptance checks',2)
for item in ['Owner login, teleport and a newly created character builder.','Resource perfect/create commands and the updated resource deed.','Training, surrender, the 1,000-point budget and persistence after relogging.','Normal crafting, experimentation and factory production timing.','House/deed placement, storage, maintenance and persistence.','Two clients, free cursor, trade and grouping; account concurrency as needed.','The adapted Han/Chewbacca quest and one-time reward.','Standard JTL ship launch, flight, combat, docking and relogging.']:
    para('- '+item)

appendices=[('Historical baseline review','SWG-developer-baseline.md'),('Original content and setup research','SWG-content-research.md'),('Initial missing-content reference inventory','SWG-content-warning-inventory.md'),('Community-content source research','SWG-community-content-shortlist.md'),('Earlier crafting and client instructions','SWG-crafting-and-client-settings.md')]
for title,name in appendices:
    story.append(PageBreak());heading('Appendix: '+title)
    para('Historical snapshot. Later sandbox/current-state chapters supersede earlier statements such as disabled JTL, 30,000-unit resource deeds, or no content installed. Original findings are preserved here to record the progression of the work.','Quote')
    markdown((OUT/name).read_text(encoding='utf-8'),demote=True)

story.append(PageBreak());heading('Appendix: operational file index')
table(['File / folder','Purpose'],[
['outputs/Start SWG Server.cmd','Start MariaDB and the galaxy; refresh address; keep WSL available.'],['outputs/Stop SWG Server.cmd','Graceful save and stop.'],['outputs/Play SWG.cmd','Start the game client.'],['outputs/Back Up SWG Galaxy.cmd','Verified galaxy recovery snapshot.'],['outputs/SWG-login.txt','Private owner credentials; contents omitted from this export.'],['outputs/SWG-client/','Client executable, assets, configuration and profiles.'],['outputs/Backups/','Verified baseline and pre-sandbox snapshots; private configuration included in those snapshots.'],['outputs/Community-content/MTG-assets/','23 downloaded asset archives and their manifest.'],['outputs/Community-content/MTG-published-content.zip','Published MTG source/content bundle.'],['outputs/Community-content/SR-public-scripts-reference.zip','Reference source; restricted-notice additions excluded.'],['outputs/Community-content/Local-sandbox-changes.zip','Changed source and public sandbox profile; credentials omitted.'],['outputs/Documentation-support/','Startup log, tracked source patch and evidence index.'],['outputs/SWG-sandbox-settings.json','Exact profile and changed-file list.'],['outputs/SWG-community-install.json','Imported catalog, loaders, quest and validation counts.'],['outputs/SWG-sandbox-validation.json','Startup, warnings, asset-copy hashes and executable hash.'],['/opt/swg/Core3/MMOCoreORB','Live server source, scripts, executable, configuration and world saves.'],['/opt/swg/tre','Server asset archives.'],['/opt/swg/sandbox-build.log','Sandbox compiler log.'],['/etc/systemd/system/swg-local.service','Game service definition.']])
para('Final server executable SHA-256: '+validation['compiled_executable_sha256'],'Mono')
heading('Implementation helper index',2)
helpers=sorted(x.name for x in (BASE/'work').glob('*.py'))
for name in helpers:para(name,'Small')
para('These helpers record preparation, audits, configuration, backups, repairs, source changes, collection, validation and document generation. They are not all intended to be rerun: several intentionally refuse duplicate application. Use the named everyday shortcuts for normal operation.','Small')

story.append(PageBreak());heading('Appendix: retrieved conversation record')
para('User and assistant messages retrieved from this chat, ordered by turn and message sequence. Some historical message text was subject to the retrieval limit; ambient browser context and passwords are omitted. This appendix is supporting conversation evidence, while the project chapters and manifests record the completed technical work. Tool outputs and internal reasoning are not a literal part of this export.','Quote')
messages=json.loads((BASE/'work/project-chat-messages.json').read_text(encoding='utf-8'))
for number,message in enumerate(messages,1):
    text=message['text'].strip()
    if not text:continue
    if '<send_user_message_question_reply>' in text:
        match=re.search(r'<send_user_message_question_reply>\s*(.*?)\s*</send_user_message_question_reply>',text,re.S)
        try:
            replies=json.loads(match[1]);text='\n\n'.join('Question: '+x.get('question','')+'\n\nAnswer: '+x.get('answer','') for x in replies)
        except Exception:text=re.sub(r'<[^>]+>','',text)
    text=re.sub(r'<external_codex_apps_open_page>.*?</external_codex_apps_open_page>','',text,flags=re.S)
    if not text.strip():continue
    text=re.sub(r'(?m)^#{1,6}\s+(.+)$',r'**\1**',text)
    role='User' if message['role']=='userMessage' else 'Assistant'
    story.append(p(str(number)+'. '+role,'BookH3'))
    markdown(text,demote=True,skip_title=False)

doc=Book(TARGET)
doc.multiBuild(story)
reader=PdfReader(str(TARGET))
pages=len(reader.pages)
texts=[page.extract_text() or '' for page in reader.pages]
if any(not t.strip() for t in texts):raise RuntimeError('Unexpected empty PDF page.')
whole='\n'.join(texts)
for phrase in ['Exact sandbox settings','MTG Content Library','Backups','Current warning inventory']:
    if phrase not in whole:raise RuntimeError('Expected document content absent: '+phrase)
(TEMP/'pdf-text.txt').write_text(whole,encoding='utf-8')
(TEMP/'pdf-validation.json').write_text(json.dumps({'pages':pages,'bytes':TARGET.stat().st_size,'all_pages_have_text':True,'title':reader.metadata.title,'pdf':str(TARGET)},indent=2),encoding='utf-8')
print(json.dumps({'pages':pages,'bytes':TARGET.stat().st_size,'pdf':str(TARGET)}))
