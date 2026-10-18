; SWG friends installer (Inno Setup 6.3 or later). Build it with build.ps1, which writes build\settings.iss and
; build\settings.json from owner-settings.json and checks the client patch kit first. Never compile it by hand
; with a settings file you have not checked: the address in it goes into every copy you hand out.
;
; What it contains: our own files only (friend-setup.ps1, the client patch kit with local_planets.tre, the
; server address, MTG-CREDITS.txt). No SOE client files, no Tailscale key, no Tailscale installer (downloaded and
; signature-checked at install time), no MTG archives: the ones a friend lacks are downloaded from MtgBaseUrl
; (mtg-share.py on Miniverse, over Tailscale) and checked against the kit manifest's sha256.

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
WelcomeLabel2=This sets up your PC to play on the owner's Star Wars Galaxies test server:%n%n- checks your SWGEmu client%n- installs Tailscale (a free private network) and joins the owner's network with your invite key%n- downloads any Mod The Galaxy archives your client is missing from Miniverse%n- adds the server's new planets and the Hutt to your client%n- points your client at the server and adds a desktop shortcut%n%nClose the game before you continue. The Mod The Galaxy archives are the MTG community's work: see MTG-CREDITS.txt.
FinishedLabel=Setup has finished.

[Files]
Source: "friend-setup.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\settings.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "FRIENDS-README.md"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme
Source: "MTG-CREDITS.txt"; DestDir: "{app}"; Flags: ignoreversion
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
  DownloadPage: TDownloadWizardPage;
  ProbeText: String;
  MtgNeeded: Boolean;

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

{ The MTG archives to download, one per line: url, file name, sha256 (tab-separated), written by -Action Check. }
function MtgListFile: String;
begin
  Result := ExpandConstant('{tmp}\mtg-needed.txt');
end;

{ Cuts S at the first tab: returns the part before it and leaves the rest in S. }
function NextField(var S: String): String;
var
  P: Integer;
begin
  P := Pos(#9, S);
  if P = 0 then
  begin
    Result := S;
    S := '';
  end
  else
  begin
    Result := Copy(S, 1, P - 1);
    Delete(S, 1, P);
  end;
end;

{ On Install: join the owner's network (Tailscale), then download the MTG archives the client lacks into Setup's temp folder. }
function JoinAndDownload: Boolean;
var
  Kind, Msg, KeyFile, Line, Url, Name: String;
  Lines: TArrayOfString;
  I: Integer;
begin
  Result := False;
  DownloadPage.Show;
  try
    { The key goes to a file in Setup's private temp folder; the helper reads and deletes it. }
    DownloadPage.SetText('Installing Tailscale and joining the owner''s network...', 'This can take a minute.');
    KeyFile := ExpandConstant('{tmp}\invite.txt');
    if Trim(KeyPage.Values[0]) <> '' then
      SaveStringToFile(KeyFile, Trim(KeyPage.Values[0]), False);
    KeyPage.Values[0] := '';
    if RunHelper(ExpandConstant('{tmp}'), '-Action Tailscale -KeyFile "' + KeyFile + '" ' + TmpArgs, Kind, Msg) <> 0 then
    begin
      DeleteFile(KeyFile);
      MsgBox(Msg, mbError, MB_OK);
      exit;
    end;
    DeleteFile(KeyFile);

    if MtgNeeded and LoadStringsFromFile(MtgListFile, Lines) then
    begin
      DownloadPage.Clear;
      for I := 0 to GetArrayLength(Lines) - 1 do
      begin
        Line := Lines[I];
        Url := NextField(Line);
        Name := NextField(Line);
        if (Url <> '') and (Name <> '') then
          DownloadPage.Add(Url, Name, Trim(Line));
      end;
      try
        DownloadPage.Download;
      except
        if DownloadPage.AbortedByUser then
          MsgBox('Download stopped. Click Install to start it again.', mbInformation, MB_OK)
        else
          MsgBox('Downloading ' + DownloadPage.LastBaseNameOrUrl + ' failed: ' + GetExceptionMessage + #13#10#13#10 +
            'The owner''s PC must be on and sharing the MTG archives. Click Install to try again, or message the owner.', mbError, MB_OK);
        exit;
      end;
    end;
    Result := True;
  finally
    DownloadPage.Hide;
  end;
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
    'The server also needs the Mod The Galaxy archives (mtg_patch_001 to mtg_patch_023 and mtg_planets.tre) in it. Setup checks them on Next ' +
    'and downloads any that are missing from the owner''s PC.',
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

  DownloadPage := CreateDownloadPage('Joining the owner''s network',
    'Setup joins the owner''s private network, then downloads the Mod The Galaxy archives your client is missing from the owner''s PC.', nil);
  DownloadPage.ShowBaseNameInsteadOfUrl := True;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Kind, Msg, Key: String;
  Code: Integer;
begin
  Result := True;
  if CurPageID = ClientPage.ID then
  begin
    WizardForm.NextButton.Enabled := False;
    try
      DeleteFile(MtgListFile);
      Code := RunHelper(ExpandConstant('{tmp}'), '-Action Check -ClientDir "' + GetClientDir('') + '" -MtgListFile "' + MtgListFile + '" ' + TmpArgs, Kind, Msg);
      { 4: archives to download after joining the network; the helper wrote the list. }
      MtgNeeded := Code = 4;
      if Code = 4 then
        MsgBox(Msg, mbInformation, MB_OK)
      else if Code <> 0 then
      begin
        MsgBox(Msg, mbError, MB_OK);
        Result := False;
      end;
    finally
      WizardForm.NextButton.Enabled := True;
    end;
  end
  else if CurPageID = wpReady then
    Result := JoinAndDownload
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
  Kind, Msg: String;
begin
  Result := '';
  { Tailscale and the MTG download already ran on the Ready page (JoinAndDownload). }
  if MtgNeeded then
  begin
    WizardForm.PreparingLabel.Caption := 'Moving the Mod The Galaxy archives into your client...';
    if RunHelper(ExpandConstant('{tmp}'), '-Action PlaceMtg -ClientDir "' + GetClientDir('') + '" -From "' + ExpandConstant('{tmp}') + '" ' + TmpArgs, Kind, Msg) <> 0 then
    begin
      Result := Msg;
      exit;
    end;
  end;

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
  Exec(PowerShell, '-NoProfile -ExecutionPolicy Bypass -File "' + App + '\friend-setup.ps1" -Action Uninstall', App, SW_HIDE, ewWaitUntilTerminated, Code);
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
  Args := '-NoProfile -ExecutionPolicy Bypass -File "' + App + '\friend-setup.ps1" ';
  Choice := TaskDialogMsgBox('Tailscale',
    'Setup installed or used Tailscale to reach the owner''s server. What should happen to it?',
    mbConfirmation, MB_YESNOCANCEL, ['Keep Tailscale as it is', 'Log out of the owner''s network', 'Remove Tailscale from this PC'], 0);
  if Choice = IDNO then
    Exec(PowerShell, Args + '-Action TailscaleLogout', App, SW_HIDE, ewWaitUntilTerminated, Code)
  else if Choice = IDCANCEL then
    Exec(PowerShell, Args + '-Action TailscaleRemove', App, SW_HIDE, ewWaitUntilTerminated, Code);
end;
