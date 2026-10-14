
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Text;
using System.Windows.Forms;
using Microsoft.Win32;

// 完全自绘的无边框窗口：没有任何子控件 => UIA 拿不到控件树，
// 只能靠图像模板 / OCR 定位文本像素位（F14.2 二级/三级策略）。
class OwnerDrawInstaller : Form {
    int step = 0;
    Rectangle btnNext, btnAccept, chkAgree;
    bool agreed = false;
    bool dark;
    public OwnerDrawInstaller(bool isDark, string title) {
        dark = isDark;
        Text = title;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        StartPosition = FormStartPosition.CenterScreen;
        ClientSize = new Size(560, 380);
        MaximizeBox = false; MinimizeBox = false;
        SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.OptimizedDoubleBuffer, true);
        btnNext = new Rectangle(400, 320, 130, 34);
        chkAgree = new Rectangle(40, 250, 20, 20);
    }
    Color Bg { get { return dark ? Color.FromArgb(32, 32, 32) : Color.FromArgb(240, 240, 240); } }
    Color Fg { get { return dark ? Color.FromArgb(240, 240, 240) : Color.FromArgb(20, 20, 20); } }
    protected override void OnPaint(PaintEventArgs e) {
        var g = e.Graphics;
        g.SmoothingMode = SmoothingMode.AntiAlias;
        g.Clear(Bg);
        using (var f = new Font("Microsoft YaHei UI", 11, FontStyle.Regular))
        using (var fb = new Font("Microsoft YaHei UI", 11, FontStyle.Bold))
        using (var b = new SolidBrush(Fg)) {
            if (step == 0) {
                g.DrawString("欢迎使用 自绘界面 安装向导", new Font("Microsoft YaHei UI", 15, FontStyle.Bold), b, 36, 36);
                g.DrawString("本窗口没有任何标准控件，UIA 无法枚举。", f, b, 36, 90);
                g.DrawString("请勾选【我接受协议】后点击【下一步】。", f, b, 36, 125);
                g.DrawRectangles(new Pen(Fg, 2), new[] { new RectangleF(chkAgree.X, chkAgree.Y, chkAgree.Width, chkAgree.Height) });
                if (agreed) {
                    using (var p = new Pen(Color.FromArgb(0, 120, 215), 3))
                        g.DrawLines(p, new[] { new Point(chkAgree.X + 4, chkAgree.Y + 10), new Point(chkAgree.X + 9, chkAgree.Y + 15), new Point(chkAgree.X + 16, chkAgree.Y + 4) });
                }
                g.DrawString("我接受协议  /  I accept the agreement", f, b, 70, 249);
                DrawButton(g, btnNext, "下一步  Next", fb);
            } else if (step == 1) {
                g.DrawString("选择安装位置", new Font("Microsoft YaHei UI", 15, FontStyle.Bold), b, 36, 36);
                g.DrawString("目标文件夹：C:\\Program Files\\ATOwnerDraw", f, b, 36, 90);
                g.DrawString("点击【安装】开始安装。", f, b, 36, 125);
                DrawButton(g, btnNext, "安装  Install", fb);
            } else {
                g.DrawString("安装完成", new Font("Microsoft YaHei UI", 15, FontStyle.Bold), b, 36, 36);
                g.DrawString("软件已成功安装到本机。", f, b, 36, 90);
                DrawButton(g, btnNext, "完成  Finish", fb);
            }
        }
        using (var p = new Pen(Color.FromArgb(0, 120, 215), 1))
            g.DrawRectangle(p, 0, 0, ClientSize.Width - 1, ClientSize.Height - 1);
    }
    void DrawButton(Graphics g, Rectangle r, string text, Font f) {
        using (var b = new LinearGradientBrush(r, Color.FromArgb(0, 120, 215), Color.FromArgb(0, 90, 170), 90f))
            g.FillRectangle(b, r);
        using (var sf = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center })
        using (var w = new SolidBrush(Color.White))
            g.DrawString(text, f, w, r, sf);
    }
    protected override void OnMouseDown(MouseEventArgs e) {
        if (btnNext.Contains(e.Location)) {
            step++;
            if (step == 2) DoInstall();
            Invalidate();
        } else if (chkAgree.Contains(e.Location)) {
            agreed = !agreed; Invalidate();
        }
    }
    void DoInstall() {
        try {
            string loc = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "ATOwnerDraw");
            Directory.CreateDirectory(loc);
            for (int i = 0; i < 10; i++) File.WriteAllText(Path.Combine(loc, "f" + i + ".dat"), new string('G', 4096));
            using (var k = Registry.CurrentUser.CreateSubKey(@"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ATOwnerDraw")) {
                k.SetValue("DisplayName", "ATOwnerDraw Synthetic");
                k.SetValue("DisplayVersion", "1.0.0");
                k.SetValue("InstallLocation", loc);
            }
        } catch { }
    }
    [STAThread]
    static void Main(string[] args) {
        try {
            Directory.CreateDirectory(@"C:\Users\Public\AT-SENTINEL");
            File.AppendAllText(@"C:\Users\Public\AT-SENTINEL\ran.log", DateTime.Now + "  OWNERDRAW\r\n");
        } catch { }
        bool dark = args.Length > 0 && args[0] == "dark";
        Application.EnableVisualStyles();
        Application.Run(new OwnerDrawInstaller(dark, "自绘界面安装向导 Synthetic"));
    }
}
