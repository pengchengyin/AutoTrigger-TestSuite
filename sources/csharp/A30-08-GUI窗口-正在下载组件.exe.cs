
using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;
using System.Threading;

// 标准 WinForms 窗口，标题与内容都指向"正在下载组件"。
// 期望：F14.4 识别到"正在下载"语义 -> 记录 requires_network，并按静默期超时处理（A15）。
class DownloadWaiter : Form {
    ProgressBar bar;
    public DownloadWaiter() {
        Text = "正在下载组件...  Downloading components";
        ClientSize = new Size(460, 180);
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false; MinimizeBox = false;
        var lbl = new Label();
        lbl.Text = "正在从 Internet 下载所需组件，请稍候...\r\nDownloading required components from the Internet";
        lbl.SetBounds(20, 20, 420, 60);
        bar = new ProgressBar();
        bar.SetBounds(20, 90, 420, 24);
        bar.Style = ProgressBarStyle.Marquee;
        Controls.Add(lbl);
        Controls.Add(bar);
    }
    [STAThread]
    static void Main(string[] args) {
        try {
            Directory.CreateDirectory(@"C:\Users\Public\AT-SENTINEL");
            File.AppendAllText(@"C:\Users\Public\AT-SENTINEL\ran.log",
                DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  A30-08-DOWNLOAD-WINDOW\r\n");
        } catch { }
        Application.Run(new DownloadWaiter());
    }
}
