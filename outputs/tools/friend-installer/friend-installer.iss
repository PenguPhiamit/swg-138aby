; SWG friends installer (Inno Setup 6.3 or later). Build it with build.ps1, which writes build\settings.iss and
; build\settings.json from owner-settings.json and checks the client patch kit first. Never compile it by hand
; with a settings file you have not checked: the address in it goes into every copy you hand out.
;
; What it contains: our own files only (friend-setup.ps1, the client patch kit with local_planets.tre, the
; server address). No SOE client files, no MTG archives, no Tailscale key, no Tailscale installer (downloaded and
; signature-checked at install time).

#include "build\settings.iss"

[Setup]
AppId={{6E3B4C1A-9D2F-4B7E-8A51-3C0F2D9B7E64}
AppName=SWG Friends Galaxy
AppVersion={#KitVersion}
AppVerName=SWG Friends Galaxy {#KitVersion}
AppPublisher=The server owner
DefaultDirName={autopf}\SWG Friends Galaxy
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=no
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible or arm64
ArchitecturesInstallIn64BitMode=x64compatible or arm64
OutputDir=build\out
OutputBaseFilename=SWG-Friends-Setup-{#KitVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName=SWG Friends Galaxy (test server)
SetupLogging=no
CloseApplications=no

[Messages]
WelcomeLabel2=This sets up your PC to play on the owner's Star Wars Galaxies test server:%n%n- checks your SWGEmu client and its Mod The Galaxy archives%n- installs Tailscale (a free private network) and joins the owner's network with your invite key%n- adds the server's new planets and the Hutt to your client%n- points your client at the server and adds a desktop shortcut%n%nClose the game before you continue. Nothing from SOE or MTG is inside this installer.
FinishedLabel=Setup has finished.

[Files]
Source: "friend-setup.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\settings.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "FRIENDS-README.md"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme
Source: "{#KitDir}\local_planets.tre"; DestDir: "{app}\kit"; Flags: ignoreversion
Source: "{#KitDir}\manifest.json"; DestDir: "{app}\kit"; Flags: ignoreversion
Source: "{#KitDir}\Install-ClientPatch.ps1"; DestDir: "{app}\kit"; Flags: ignoreversion
Source: "{#KitDir}\Uninstall-ClientPatch.ps1"; DestDir: "{app}\kit"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\Play SWG (owner's server)"; Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File ""{app}\friend-setup.ps1"" -Action Play"; WorkingDir: "{app}"; IconFilename: "{code:GetClientDir}\SWGEmu.exe"

[UninstallDelete]
Type: files; Name: "{app}\state.json"
Type: dirifempty; Name: "{app}\kit"
Type: dirifempty; Name: "{app}"

[Code]
var
  ClientPage: TInputDirWizardPage;
  KeyPage: TInputQueryWizardPage;
  ProbeText: String;

function PowerShell: String;
begin
  Result := ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe');
end;

{ Runs friend-setup.ps1 from Dir; Msg gets the helper's message; returns its exit code (or -1). }
function RunHelper(Dir, Args: String; var Kind, Msg: String): Integer;
var
  ResultFile: String;
  Lines: TArrayOfString;
  I, Code: Integer;
begin
  ResultFile := ExpandConstant('{tmp}\result.txt');
  DeleteFile(ResultFile);
  Kind := 'ERR';
  Msg := 'The setup helper did not run.';
  if not Exec(PowerShell, '-NoProfile -ExecutionPolicy Bypass -File "' + Dir + '\friend-setup.ps1" ' + Args +
      ' -ResultFile "' + ResultFile + '"', Dir, SW_HIDE, ewWaitUntilTerminated, Code) then
  begin
    Result := -1;
    exit;
  end;
  Result := Code;
  if LoadStringsFromFile(ResultFile, Lines) and (GetArrayLength(Lines) > 0) then
  begin
    Kind := Trim(Lines[0]);
    Msg := '';
    for I := 1 to GetArrayLength(Lines) - 1 do
    begin
      if Msg <> '' then Msg := Msg + #13#10;
      Msg := Msg + Lines[I];
    end;
  end;
end;

// Helper, settings and kit in the temp folder, for the checks and the install steps that run before files are copied.
procedure ExtractAll;
begin
  ExtractTemporaryFile('friend-setup.ps1');
  ExtractTemporaryFile('settings.json');
  ExtractTemporaryFile('manifest.json');
  ExtractTemporaryFile('Install-ClientPatch.ps1');
  ExtractTemporaryFile('Uninstall-ClientPatch.ps1');
end;

function TmpArgs: String;
begin
  Result := '-SettingsFile "' + ExpandConstant('{tmp}\settings.json') + '" -KitDir "' + ExpandConstant('{tmp}') +
    '" -StateFile "' + AddBackslash(WizardDirValue) + 'state.json"';
end;

function GetClientDir(Param: String): String;
begin
  Result := RemoveBackslashUnlessRoot(ClientPage.Values[0]);
end;

procedure InitializeWizard;
var
  Kind, Msg: String;
  Lines: TArrayOfString;
begin
  ExtractAll;
  ClientPage := CreateInputDirPage(wpWelcome, 'Your SWGEmu client',
    'Where is the folder with SWGEmu.exe in it?',
    'Setup looked for your SWGEmu client. Check the folder below, or click Browse and pick the one that holds SWGEmu.exe.' + #13#10#13#10 +
    'It must also have the Mod The Galaxy archives (mtg_patch_001 to mtg_patch_023 and mtg_planets.tre). Setup checks them on Next.',
    False, '');
  ClientPage.Add('');
  ClientPage.Values[0] := 'C:\SWGEmu';
  if RunHelper(ExpandConstant('{tmp}'), '-Action Detect ' + TmpArgs, Kind, Msg) = 0 then
    if Msg <> '' then
    begin
      if Pos(#13#10, Msg) > 0 then Msg := Copy(Msg, 1, Pos(#13#10, Msg) - 1);
      ClientPage.Values[0] := Msg;
    end;

  KeyPage := CreateInputQueryPage(ClientPage.ID, 'Your invite key',
    'Paste the invite key the server owner sent you.',
    'The key lets this PC join the owner''s private Tailscale network, the only way to reach the server. It starts with tskey- and works once.' + #13#10#13#10 +
    'Setup uses it once and does not keep it. If this PC is already on the owner''s network, leave it empty.');
  KeyPage.Add('Invite key:', True);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Kind, Msg, Key: String;
begin
  Result := True;
  if CurPageID = ClientPage.ID then
  begin
    WizardForm.NextButton.Enabled := False;
    try
      if RunHelper(ExpandConstant('{tmp}'), '-Action Check -ClientDir "' + GetClientDir('') + '" ' + TmpArgs, Kind, Msg) <> 0 then
      begin
        MsgBox(Msg, mbError, MB_OK);
        Result := False;
      end;
    finally
      WizardForm.NextButton.Enabled := True;
    end;
  end
  else if CurPageID = KeyPage.ID then
  begin
    Key := Trim(KeyPage.Values[0]);
    if (Key <> '') and (Pos('tskey-', Key) <> 1) then
    begin
      MsgBox('That does not look like an invite key. It starts with tskey-. Copy the whole key from the owner''s message.', mbError, MB_OK);
      Result := False;
    end
    else if Key = '' then
    begin
      if RunHelper(ExpandConstant('{tmp}'), '-Action Probe ' + TmpArgs, Kind, Msg) <> 0 then
      begin
        MsgBox('This PC cannot reach the server yet, so Setup needs your invite key.' + #13#10#13#10 + Msg, mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  Kind, Msg, KeyFile: String;
begin
  Result := '';
  { Tailscale first: the key goes to a file in Setup's private temp folder; the helper reads and deletes it. }
  WizardForm.PreparingLabel.Caption := 'Installing Tailscale and joining the owner''s network...';
  KeyFile := ExpandConstant('{tmp}\invite.txt');
  if Trim(KeyPage.Values[0]) <> '' then
    SaveStringToFile(KeyFile, Trim(KeyPage.Values[0]), False);
  KeyPage.Values[0] := '';
  if RunHelper(ExpandConstant('{tmp}'), '-Action Tailscale -KeyFile "' + KeyFile + '" ' + TmpArgs, Kind, Msg) <> 0 then
  begin
    DeleteFile(KeyFile);
    Result := Msg;
    exit;
  end;
  DeleteFile(KeyFile);

  ExtractTemporaryFile('local_planets.tre');
  WizardForm.PreparingLabel.Caption := 'Adding the server''s planets to your client...';
  if RunHelper(ExpandConstant('{tmp}'), '-Action Patch -ClientDir "' + GetClientDir('') + '" ' + TmpArgs, Kind, Msg) <> 0 then
    Result := Msg;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Kind, Msg: String;
begin
  if CurStep = ssPostInstall then
  begin
    WizardForm.StatusLabel.Caption := 'Testing the connection to the server...';
    RunHelper(ExpandConstant('{app}'), '-Action Probe', Kind, Msg);
    ProbeText := Msg;
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
    WizardForm.FinishedLabel.Caption :=
      ProbeText + #13#10#13#10 +
      'To play: double-click "Play SWG (owner''s server)" on your desktop. Log in with any username and password you choose; ' +
      'the server makes your account the first time. Tell the owner your username.' + #13#10#13#10 +
      'Tailscale must be running (its icon by the clock). If the game cannot connect, tell the owner: the server may be off.';
end;

function InitializeUninstall: Boolean;
var
  Code: Integer;
  App: String;
begin
  { Put the client back first; stop if the game is running, so nothing is half removed. }
  Result := True;
  App := ExpandConstant('{app}');
  Exec(PowerShell, '-NoProfile -ExecutionPolicy Bypass -File "' + App + 'riend-setup.ps1" -Action Uninstall', App, SW_HIDE, ewWaitUntilTerminated, Code);
  if Code = 5 then
  begin
    MsgBox('The game is running. Close it, then uninstall again.', mbError, MB_OK);
    Result := False;
  end
  else if Code <> 0 then
    Result := MsgBox('Your client could not be fully changed back (code ' + IntToStr(Code) + '). Remove the rest anyway?', mbConfirmation, MB_YESNO) = IDYES;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Code, Choice: Integer;
  App, Args: String;
begin
  if (CurUninstallStep <> usUninstall) or UninstallSilent then exit;
  App := ExpandConstant('{app}');
  Args := '-NoProfile -ExecutionPolicy Bypass -File "' + App + 'riend-setup.ps1" ';
  Choice := TaskDialogMsgBox('Tailscale',
    'Setup installed or used Tailscale to reach the owner''s server. What should happen to it?',
    mbConfirmation, MB_YESNOCANCEL, ['Keep Tailscale as it is', 'Log out of the owner''s network', 'Remove Tailscale from this PC'], 0);
  if Choice = IDNO then
    Exec(PowerShell, Args + '-Action TailscaleLogout', App, SW_HIDE, ewWaitUntilTerminated, Code)
  else if Choice = IDCANCEL then
    Exec(PowerShell, Args + '-Action TailscaleRemove', App, SW_HIDE, ewWaitUntilTerminated, Code);
end;
