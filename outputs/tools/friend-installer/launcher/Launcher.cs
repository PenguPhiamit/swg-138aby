// SWG: Fractured Galaxy launcher and updater. Friends start the game from here.
//
// On open it checks, in the background:
//   - the server: one SOE session request to the login port (the same probe as friend-setup.ps1 -Action Probe);
//   - the owner's update server (mtg-share.py, over Tailscale): update.json lists the local_planets.tre the server
//     loads right now, the MTG archives, the newest launcher and a news line;
//   - the client: local_planets.tre against the server's sha256, the MTG archives by size, the .include line in
//     swgemu.cfg and the login lines in swgemu_login.cfg.
// Then it brings the client in line: every download goes to a .part file and is checked against its sha256 before
// it replaces anything; the old local_planets.tre is kept in local_planets-patch\backup\<version>. MTG archives
// go through friend-setup.ps1 -Action PlaceMtg, so the uninstaller knows what to undo. A newer launcher replaces
// this exe (renamed to .old) and restarts. Play stays off while the client's patch differs from the server's.
//
// Built by build.ps1 with the C# compiler that ships with Windows (.NET Framework 4, C# 5): no downloads.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;

[assembly: AssemblyTitle("SWG: Fractured Galaxy")]
[assembly: AssemblyProduct("SWG: Fractured Galaxy launcher")]
[assembly: AssemblyVersion("1.0.0.0")]

namespace FracturedGalaxy
{
    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
            Application.Run(new LauncherForm(args));
        }
    }

    class LauncherForm : Form
    {
        const string LoginMarker = "; Written by the SWG friends installer";
        static readonly Encoding Latin1 = Encoding.GetEncoding(28591);
        static readonly Color CBack = Color.FromArgb(14, 12, 16);
        static readonly Color CPanel = Color.FromArgb(26, 22, 28);
        static readonly Color CText = Color.FromArgb(232, 226, 214);
        static readonly Color CDim = Color.FromArgb(150, 142, 132);
        static readonly Color CAccent = Color.FromArgb(196, 48, 32);
        static readonly Color CGood = Color.FromArgb(92, 190, 110);
        static readonly Color CWarn = Color.FromArgb(230, 170, 70);

        readonly string appDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\');
        readonly bool dryRun;
        Dictionary<string, object> settings;
        string clientDir;
        Label serverLabel, filesLabel, newsLabel, stepLabel;
        ProgressBar bar;
        Button playButton, verifyButton;
        volatile bool busy;
        bool serverUp, filesReady;

        public LauncherForm(string[] args)
        {
            dryRun = Array.IndexOf(args, "--dry-run") >= 0;
            Text = "SWG: Fractured Galaxy";
            BackColor = CBack;
            ForeColor = CText;
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;
            StartPosition = FormStartPosition.CenterScreen;
            ClientSize = new Size(960, 520);
            Font = new Font("Segoe UI", 10f);
            try { Icon = Icon.ExtractAssociatedIcon(Assembly.GetExecutingAssembly().Location); } catch { }

            var banner = new PictureBox { Location = new Point(0, 0), Size = new Size(960, 320), SizeMode = PictureBoxSizeMode.Zoom, BackColor = Color.Black };
            banner.Image = LoadBanner();
            Controls.Add(banner);

            var panel = new Panel { Location = new Point(0, 320), Size = new Size(960, 200), BackColor = CPanel };
            Controls.Add(panel);
            serverLabel = AddLabel(panel, 24, 16, 600, "Server: checking...");
            filesLabel = AddLabel(panel, 24, 44, 600, "Your files: checking...");
            newsLabel = AddLabel(panel, 24, 72, 640, "");
            newsLabel.ForeColor = CDim;
            newsLabel.Height = 48;
            stepLabel = AddLabel(panel, 24, 128, 640, "");
            stepLabel.ForeColor = CDim;
            bar = new ProgressBar { Location = new Point(24, 156), Size = new Size(640, 18), Style = ProgressBarStyle.Continuous };
            panel.Controls.Add(bar);

            playButton = new Button { Text = "PLAY", Location = new Point(700, 24), Size = new Size(236, 72), Enabled = false,
                FlatStyle = FlatStyle.Flat, BackColor = CAccent, ForeColor = Color.White, Font = new Font("Segoe UI Semibold", 18f) };
            playButton.FlatAppearance.BorderSize = 0;
            playButton.Click += delegate { Play(); };
            panel.Controls.Add(playButton);
            verifyButton = new Button { Text = "Check all files", Location = new Point(700, 112), Size = new Size(236, 34),
                FlatStyle = FlatStyle.Flat, BackColor = CPanel, ForeColor = CText };
            verifyButton.Click += delegate { StartCheck(true); };
            panel.Controls.Add(verifyButton);
            var folder = new LinkLabel { Text = "Open game folder", Location = new Point(700, 156), AutoSize = true, LinkColor = CDim, ActiveLinkColor = CText };
            folder.LinkClicked += delegate { if (clientDir != null) Process.Start("explorer.exe", "\"" + clientDir + "\""); };
            panel.Controls.Add(folder);

            Shown += delegate { StartCheck(false); };
        }

        Label AddLabel(Control parent, int x, int y, int w, string text)
        {
            var l = new Label { Location = new Point(x, y), Size = new Size(w, 24), Text = text, ForeColor = CText, BackColor = Color.Transparent };
            parent.Controls.Add(l);
            return l;
        }

        Image LoadBanner()
        {
            string file = Path.Combine(appDir, "banner.png");
            try { if (File.Exists(file)) return Image.FromStream(new MemoryStream(File.ReadAllBytes(file))); } catch { }
            try { return Image.FromStream(Assembly.GetExecutingAssembly().GetManifestResourceStream("banner.png")); } catch { }
            return null;
        }

        // --- UI from the worker thread ----------------------------------------------------------------------
        void Ui(Action a) { if (IsHandleCreated) BeginInvoke(a); }
        void Step(string text) { Ui(delegate { stepLabel.Text = text; }); }
        void Progress(long done, long total) { Ui(delegate { bar.Maximum = 1000; bar.Value = total > 0 ? (int)Math.Min(1000, done * 1000 / total) : 0; }); }
        void SetLabel(Label l, string text, Color c) { Ui(delegate { l.Text = text; l.ForeColor = c; }); }
        void UpdatePlay() { Ui(delegate { playButton.Enabled = !busy && filesReady && clientDir != null; }); }

        void StartCheck(bool deep)
        {
            if (busy) return;
            busy = true;
            playButton.Enabled = false;
            verifyButton.Enabled = false;
            var t = new Thread(delegate ()
            {
                try { Check(deep); }
                catch (Exception e) { SetLabel(filesLabel, "Your files: something went wrong (" + e.Message + ")", CWarn); Step(""); }
                finally { busy = false; Ui(delegate { verifyButton.Enabled = true; }); UpdatePlay(); }
            });
            t.IsBackground = true;
            t.Start();
        }

        // --- the check ----------------------------------------------------------------------------------------
        void Check(bool deep)
        {
            settings = ReadJson(Path.Combine(appDir, "settings.json"));
            var state = ReadJson(Path.Combine(appDir, "state.json"));
            clientDir = Str(state, "ClientDir");
            if (settings == null || clientDir == null || !File.Exists(Path.Combine(clientDir, "SWGEmu.exe")))
            {
                SetLabel(filesLabel, "Your files: the game folder is not set up. Run SWG-Friends-Setup again.", CWarn);
                clientDir = null;
                return;
            }
            TryDelete(Assembly.GetExecutingAssembly().Location + ".old");

            Step("Checking the server...");
            string probe;
            serverUp = Probe(Str(settings, "ServerAddress"), Convert.ToInt32(settings["LoginPort"]), out probe);
            SetLabel(serverLabel, serverUp ? "Server: online" : "Server: offline (" + probe + ")", serverUp ? CGood : CWarn);

            string baseUrl = (Str(settings, "MtgBaseUrl") ?? "").TrimEnd('/');
            Dictionary<string, object> info = null;
            if (baseUrl != "")
            {
                Step("Asking Miniverse for updates...");
                try { info = new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(Encoding.UTF8.GetString(Fetch(baseUrl + "/update.json"))); }
                catch { info = null; }
            }
            if (info == null)
            {
                // No update server: play with what is installed.
                filesReady = File.Exists(Path.Combine(clientDir, "local_planets.tre"));
                SetLabel(filesLabel, "Your files: can't check for updates (Miniverse isn't sharing them right now). You can still play.", CWarn);
                Repair();
                Step("");
                return;
            }
            Ui(delegate { newsLabel.Text = Str(info, "news") ?? ""; });

            if (SelfUpdate(baseUrl, info as Dictionary<string, object>)) return;

            var plan = new List<string>();
            var patch = info.ContainsKey("patch") ? info["patch"] as Dictionary<string, object> : null;
            string tre = Path.Combine(clientDir, "local_planets.tre");
            bool patchOld = patch != null && (!File.Exists(tre) || Sha256(tre) != Str(patch, "sha256"));
            if (patchOld) plan.Add("the server patch (version " + Str(patch, "version") + ")");
            var mtg = MtgNeeds(info, deep);
            if (mtg.Count > 0) plan.Add(mtg.Count + " MTG archive(s)");

            if (plan.Count > 0 && Running())
            {
                filesReady = false;
                SetLabel(filesLabel, "Your files: an update is waiting. Close the game to install it.", CWarn);
                Step("");
                return;
            }
            if (patchOld) UpdatePatch(baseUrl, patch);
            if (mtg.Count > 0) UpdateMtg(baseUrl, mtg);
            Repair();
            filesReady = patch == null || Sha256(tre) == Str(patch, "sha256");
            SetLabel(filesLabel, filesReady ? "Your files: up to date (server patch " + (patch != null ? Str(patch, "version") : "?") + ")"
                : "Your files: the update did not finish. Click Check all files to try again.", filesReady ? CGood : CWarn);
            Step(plan.Count > 0 ? "Updated " + string.Join(" and ", plan.ToArray()) + "." : "");
            Progress(0, 0);
        }

        List<Dictionary<string, object>> MtgNeeds(Dictionary<string, object> info, bool deep)
        {
            var need = new List<Dictionary<string, object>>();
            var list = info.ContainsKey("requires") ? info["requires"] as ArrayList : null;
            if (list == null) return need;
            int i = 0;
            foreach (Dictionary<string, object> r in list)
            {
                i++;
                string p = Path.Combine(clientDir, Str(r, "file"));
                long size = Convert.ToInt64(r["size"]);
                if (!File.Exists(p) || new FileInfo(p).Length != size) { need.Add(r); continue; }
                if (deep)
                {
                    Step("Checking " + Str(r, "file") + " (" + i + " of " + list.Count + ")...");
                    if (Sha256(p) != Str(r, "sha256")) need.Add(r);
                }
            }
            return need;
        }

        void UpdatePatch(string baseUrl, Dictionary<string, object> patch)
        {
            string tre = Path.Combine(clientDir, "local_planets.tre");
            string sha = Str(patch, "sha256");
            string part = tre + ".part";
            Step("Downloading the server patch...");
            if (!Download(baseUrl + "/local_planets.tre", part, Convert.ToInt64(patch["size"]), sha)) return;
            if (dryRun) { TryDelete(part); Step("DRY RUN: would replace local_planets.tre"); return; }
            string patchDir = Path.Combine(clientDir, "local_planets-patch");
            var kitState = ReadJson(Path.Combine(patchDir, "state.json")) ?? new Dictionary<string, object>();
            string old = Str(kitState, "version") ?? "unknown";
            if (File.Exists(tre))
            {
                string keep = Path.Combine(patchDir, "backup\\" + old);
                Directory.CreateDirectory(keep);
                string saved = Path.Combine(keep, "local_planets.tre");
                if (!File.Exists(saved)) File.Copy(tre, saved);
                File.Delete(tre);
            }
            File.Move(part, tre);
            // The kit's record, so its uninstaller still recognises the archive as ours.
            kitState["previous"] = old;
            kitState["version"] = Str(patch, "version");
            kitState["sha256"] = sha;
            kitState["installed"] = DateTime.Now.ToString("yyyy-MM-dd h:mm tt") + " (launcher)";
            Directory.CreateDirectory(patchDir);
            File.WriteAllText(Path.Combine(patchDir, "state.json"), new JavaScriptSerializer().Serialize(kitState), Encoding.ASCII);
        }

        void UpdateMtg(string baseUrl, List<Dictionary<string, object>> need)
        {
            long total = 0;
            foreach (var r in need) total += Convert.ToInt64(r["size"]);
            string tmp = Path.Combine(Path.GetTempPath(), "fractured-galaxy-mtg");
            Directory.CreateDirectory(tmp);
            int i = 0;
            foreach (var r in need)
            {
                i++;
                string name = Str(r, "file");
                string dest = Path.Combine(tmp, name);
                Step(string.Format("Downloading {0} ({1} of {2}, {3:N1} GB in all)...", name, i, need.Count, total / 1073741824.0));
                if (File.Exists(dest) && new FileInfo(dest).Length == Convert.ToInt64(r["size"]) && Sha256(dest) == Str(r, "sha256")) continue;
                if (!Download(baseUrl + "/" + Uri.EscapeDataString(name), dest + ".part", Convert.ToInt64(r["size"]), Str(r, "sha256"))) return;
                File.Move(dest + ".part", dest);
            }
            // A file with a different version in the client is not "missing" to PlaceMtg; move ours aside first
            // only through PlaceMtg, which keeps the friend's copy for the uninstaller.
            Step("Placing the MTG archives...");
            if (dryRun) { Step("DRY RUN: would place " + need.Count + " MTG archive(s)"); return; }
            string ps = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System), "WindowsPowerShell\\v1.0\\powershell.exe");
            var p = Process.Start(new ProcessStartInfo(ps, "-NoProfile -ExecutionPolicy Bypass -File \"" + Path.Combine(appDir, "friend-setup.ps1") +
                "\" -Action PlaceMtg -ClientDir \"" + clientDir + "\" -From \"" + tmp + "\"") { CreateNoWindow = true, UseShellExecute = false });
            p.WaitForExit();
            if (p.ExitCode == 0) { try { Directory.Delete(tmp, true); } catch { } }
            else Step("The MTG archives were downloaded but could not be placed (code " + p.ExitCode + "). Close the game and try again.");
        }

        // The SWGEmu launcher may reset swgemu.cfg or swgemu_login.cfg: put our two lines back.
        void Repair()
        {
            if (dryRun) return;
            string main = Path.Combine(clientDir, "swgemu.cfg");
            if (File.Exists(main) && File.Exists(Path.Combine(clientDir, "local_planets.cfg")))
            {
                string text = File.ReadAllText(main, Latin1);
                if (!System.Text.RegularExpressions.Regex.IsMatch(text, "(?m)^\\s*\\.include\\s+\"local_planets\\.cfg\"\\s*$"))
                {
                    if (text.Length > 0 && !text.EndsWith("\n")) text += "\r\n";
                    File.WriteAllText(main, text + ".include \"local_planets.cfg\"\r\n", Latin1);
                }
            }
            string login = Path.Combine(clientDir, "swgemu_login.cfg");
            string want = LoginMarker + "; the uninstaller puts your own file back.\r\n[ClientGame]\r\nloginServerAddress0=" +
                Str(settings, "ServerAddress") + "\r\nloginServerPort0=" + Convert.ToInt32(settings["LoginPort"]) + "\r\n";
            string have = File.Exists(login) ? File.ReadAllText(login, Latin1) : "";
            if (have == want) return;
            if (have != "" && !have.StartsWith(LoginMarker))
            {
                string backup = Path.Combine(clientDir, "local_planets-patch\\backup\\friends-installer");
                Directory.CreateDirectory(backup);
                if (!File.Exists(Path.Combine(backup, "swgemu_login.cfg"))) File.Copy(login, Path.Combine(backup, "swgemu_login.cfg"));
            }
            File.WriteAllText(login, want, Latin1);
        }

        bool SelfUpdate(string baseUrl, Dictionary<string, object> info)
        {
            var l = info.ContainsKey("launcher") ? info["launcher"] as Dictionary<string, object> : null;
            if (l == null) return false;
            Version mine = Assembly.GetExecutingAssembly().GetName().Version, theirs;
            if (!Version.TryParse(Str(l, "version") ?? "", out theirs) || theirs <= mine) return false;
            string exe = Assembly.GetExecutingAssembly().Location;
            Step("Updating the launcher to " + theirs + "...");
            if (!Download(baseUrl + "/" + Str(l, "file"), exe + ".new", Convert.ToInt64(l["size"]), Str(l, "sha256"))) return false;
            if (dryRun) { TryDelete(exe + ".new"); Step("DRY RUN: would replace the launcher"); return false; }
            try
            {
                TryDelete(exe + ".old");
                File.Move(exe, exe + ".old");       // Windows lets a running exe be renamed, not overwritten
                File.Move(exe + ".new", exe);
                Process.Start(exe);
                Ui(delegate { Close(); });
                return true;
            }
            catch (Exception e) { Step("Could not update the launcher (" + e.Message + "); carrying on with this one."); return false; }
        }

        // --- play -----------------------------------------------------------------------------------------
        void Play()
        {
            if (Running()) { MessageBox.Show(this, "The game is already running.", Text); return; }
            if (!serverUp && MessageBox.Show(this, "The server is not answering. It may be off, or Tailscale is not connected (its icon by the clock).\r\n\r\nStart the game anyway?",
                Text, MessageBoxButtons.YesNo, MessageBoxIcon.Warning) != DialogResult.Yes) return;
            Repair();
            if (dryRun) { MessageBox.Show(this, "DRY RUN: would start " + Path.Combine(clientDir, "SWGEmu.exe"), Text); return; }
            Process.Start(new ProcessStartInfo(Path.Combine(clientDir, "SWGEmu.exe")) { WorkingDirectory = clientDir, UseShellExecute = true });
            WindowState = FormWindowState.Minimized;
        }

        bool Running()
        {
            foreach (var p in Process.GetProcesses())
            {
                string name = p.ProcessName.ToLowerInvariant();
                if (name != "swgemu" && name != "swgclient_r" && name != "swgemu_launcher") continue;
                try { if (p.MainModule.FileName.StartsWith(clientDir + "\\", StringComparison.OrdinalIgnoreCase)) return true; }
                catch { return true; }
            }
            return false;
        }

        // --- helpers ----------------------------------------------------------------------------------------
        static bool Probe(string host, int port, out string why)
        {
            // An SOE session request (00 01, CRC length 2, a random connection id, 496-byte packets); a Core3 login
            // server answers 00 02. The half-open session times out on the server.
            why = "";
            IPAddress ip = null;
            try { foreach (var a in Dns.GetHostAddresses(host)) if (a.AddressFamily == AddressFamily.InterNetwork) { ip = a; break; } }
            catch { }
            if (ip == null) { why = "can't find " + host + "; is Tailscale connected?"; return false; }
            var id = new byte[4];
            new Random().NextBytes(id);
            var pkt = new byte[] { 0, 1, 0, 0, 0, 2, id[0], id[1], id[2], id[3], 0, 0, 1, 0xF0 };
            using (var udp = new UdpClient())
            {
                udp.Client.ReceiveTimeout = 3000;
                for (int i = 0; i < 2; i++)
                {
                    try
                    {
                        udp.Send(pkt, pkt.Length, new IPEndPoint(ip, port));
                        var from = new IPEndPoint(IPAddress.Any, 0);
                        var r = udp.Receive(ref from);
                        if (r.Length >= 2 && r[0] == 0 && r[1] == 2) return true;
                    }
                    catch { }
                }
            }
            why = "no answer from " + ip + ":" + port;
            return false;
        }

        static byte[] Fetch(string url)
        {
            var req = (HttpWebRequest)WebRequest.Create(url);
            req.Timeout = 5000;
            req.ReadWriteTimeout = 5000;
            using (var resp = req.GetResponse())
            using (var s = resp.GetResponseStream())
            using (var m = new MemoryStream())
            {
                s.CopyTo(m);
                return m.ToArray();
            }
        }

        // Downloads to `part`, hashing as it goes; keeps it only if size and sha256 match.
        bool Download(string url, string part, long size, string sha)
        {
            try
            {
                var req = (HttpWebRequest)WebRequest.Create(url);
                req.Timeout = 15000;
                req.ReadWriteTimeout = 60000;
                using (var resp = req.GetResponse())
                using (var s = resp.GetResponseStream())
                using (var f = new FileStream(part, FileMode.Create, FileAccess.Write))
                using (var h = SHA256.Create())
                {
                    var buf = new byte[1 << 20];
                    long done = 0;
                    int n;
                    while ((n = s.Read(buf, 0, buf.Length)) > 0)
                    {
                        f.Write(buf, 0, n);
                        h.TransformBlock(buf, 0, n, null, 0);
                        done += n;
                        Progress(done, size);
                    }
                    h.TransformFinalBlock(buf, 0, 0);
                    if (done != size || Hex(h.Hash) != sha)
                    {
                        f.Close();
                        TryDelete(part);
                        Step("A download did not match the owner's copy, so it was thrown away. Try again later.");
                        return false;
                    }
                }
                return true;
            }
            catch (Exception e)
            {
                TryDelete(part);
                Step("Download stopped: " + e.Message);
                return false;
            }
        }

        static string Sha256(string path)
        {
            using (var h = SHA256.Create())
            using (var f = File.OpenRead(path)) return Hex(h.ComputeHash(f));
        }
        static string Hex(byte[] b) { var sb = new StringBuilder(); foreach (var x in b) sb.Append(x.ToString("x2")); return sb.ToString(); }
        static void TryDelete(string p) { try { if (File.Exists(p)) File.Delete(p); } catch { } }
        static string Str(Dictionary<string, object> d, string k) { object v; return d != null && d.TryGetValue(k, out v) && v != null ? v.ToString() : null; }
        static Dictionary<string, object> ReadJson(string path)
        {
            try { return File.Exists(path) ? new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(File.ReadAllText(path)) : null; }
            catch { return null; }
        }
    }
}
