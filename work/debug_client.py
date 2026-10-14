import ctypes as c, subprocess, time
from pathlib import Path
k=c.WinDLL('kernel32',use_last_error=True)
class Event(c.Structure):
    _fields_=[('code',c.c_ulong),('pid',c.c_ulong),('tid',c.c_ulong),('data',c.c_ulonglong*20)]
k.OpenProcess.restype=c.c_void_p
k.ReadProcessMemory.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)]
folder=Path(r'C:\Users\Pengw\Documents\Codex\2026-10-13\h\outputs\SWG-client')
p=subprocess.Popen([str(folder/'SWGEmu.exe')],cwd=folder,creationflags=2)
handle=k.OpenProcess(0x410,False,p.pid)
end=time.time()+30
while time.time()<end:
    e=Event()
    if not k.WaitForDebugEvent(c.byref(e),1000): continue
    status=0x10002
    raw=bytes(e.data)
    if e.code==8:
        pointer=int.from_bytes(raw[:8],'little'); unicode=int.from_bytes(raw[8:10],'little'); length=int.from_bytes(raw[10:12],'little')
        buf=c.create_string_buffer(length*(2 if unicode else 1)+2); count=c.c_size_t()
        if k.ReadProcessMemory(handle,pointer,buf,len(buf)-2,c.byref(count)):
            print(buf.raw[:count.value].decode('utf-16-le' if unicode else 'latin1',errors='replace').rstrip('\0'),flush=True)
    elif e.code==1:
        code=int.from_bytes(raw[:4],'little')
        if code!=0x80000003:
            print('Exception',hex(code),flush=True); status=0x80010001
    k.ContinueDebugEvent(e.pid,e.tid,status)
    if e.code==5: break
