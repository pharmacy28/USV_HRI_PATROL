using System;
using System.Globalization;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using Tobii.Gaming;
using UnityEngine;

/// <summary>
/// Unity side Tobii gaze UDP sender.
///
/// Sends one JSON packet per frame to a Python UDP-to-LSL bridge.
/// The packet includes normalized top-left-origin gaze coordinates, pixel
/// coordinates, raw Tobii values, validity, and Unity screen size.
/// </summary>
[DisallowMultipleComponent]
public class GazeUdpSender : MonoBehaviour
{
    [Serializable]
    private class GazeUdpConfig
    {
        public string target_host;
        public int target_port;
        public bool flip_viewport_y = true;
    }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void AutoCreate()
    {
        if (FindObjectOfType<GazeUdpSender>() != null)
        {
            return;
        }

        var go = new GameObject("GazeUdpSender", typeof(GazeUdpSender));
        DontDestroyOnLoad(go);
    }

    [Header("UDP")]
    [SerializeField] private string m_TargetHost = "127.0.0.1";
    [SerializeField] private int m_TargetPort = 15555;

    [Header("Coordinate handling")]
    [Tooltip("Tobii viewport Y is usually bottom-left in Unity. Enable this to publish top-left-origin y_norm.")]
    [SerializeField] private bool m_FlipViewportY = true;

    private UdpClient m_Client;
    private IPEndPoint m_EndPoint;
    private int m_FrameCount;

    private void Awake()
    {
        ApplyRuntimeConfiguration();

        try
        {
            m_Client = new UdpClient();
            m_EndPoint = new IPEndPoint(ResolveAddress(m_TargetHost), m_TargetPort);
            Debug.Log($"[EyeTracker] UDP ready -> {m_TargetHost}:{m_TargetPort}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[EyeTracker] UDP init failed: {e.Message}");
        }
    }

    private void OnDestroy()
    {
        m_Client?.Close();
        m_Client?.Dispose();
    }

    private void Update()
    {
        if (m_Client == null)
        {
            return;
        }

        try
        {
            var gazePoint = TobiiAPI.GetGazePoint();
            var valid = gazePoint.IsRecent();

            var rawScreenX = valid ? gazePoint.Screen.x : float.NaN;
            var rawScreenY = valid ? gazePoint.Screen.y : float.NaN;
            var rawViewportX = valid ? gazePoint.Viewport.x : float.NaN;
            var rawViewportY = valid ? gazePoint.Viewport.y : float.NaN;

            var normalized = ResolveNormalized(
                valid,
                rawScreenX,
                rawScreenY,
                rawViewportX,
                rawViewportY,
                Screen.width,
                Screen.height);

            valid = normalized.valid;
            var trackerTime = valid ? gazePoint.Timestamp : Time.unscaledTime;
            var trackerTimeUs = valid ? gazePoint.PreciseTimestamp : -1L;
            var xNorm = normalized.xNorm;
            var yNorm = normalized.yNorm;
            var xPx = valid ? xNorm * Screen.width : float.NaN;
            var yPx = valid ? yNorm * Screen.height : float.NaN;

            SendFrame(
                trackerTime,
                Time.unscaledTime,
                trackerTimeUs,
                valid,
                xNorm,
                yNorm,
                xPx,
                yPx,
                rawScreenX,
                rawScreenY,
                rawViewportX,
                rawViewportY,
                Screen.width,
                Screen.height);

            m_FrameCount++;

            if ((m_FrameCount % 120) == 0)
            {
                Debug.Log(
                    $"[EyeTracker] {m_FrameCount} frames | valid={(valid ? 1 : 0)} | " +
                    $"norm=({xNorm:F3},{yNorm:F3}) | px=({xPx:F0},{yPx:F0})");
            }
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"[EyeTracker] send exception: {e.Message}");
        }
    }

    private (bool valid, float xNorm, float yNorm) ResolveNormalized(
        bool valid,
        float screenX,
        float screenY,
        float viewportX,
        float viewportY,
        int screenWidth,
        int screenHeight)
    {
        if (!valid)
        {
            return (false, float.NaN, float.NaN);
        }

        if (IsUnit(viewportX) && IsUnit(viewportY))
        {
            var y = m_FlipViewportY ? 1.0f - viewportY : viewportY;
            return (true, viewportX, Mathf.Clamp01(y));
        }

        if (screenWidth > 0 && screenHeight > 0 && IsFinite(screenX) && IsFinite(screenY))
        {
            var xNorm = screenX / screenWidth;
            var yNorm = screenY / screenHeight;

            if (xNorm >= -0.05f && xNorm <= 1.05f && yNorm >= -0.05f && yNorm <= 1.05f)
            {
                return (true, Mathf.Clamp01(xNorm), Mathf.Clamp01(yNorm));
            }
        }

        return (false, float.NaN, float.NaN);
    }

    private void ApplyRuntimeConfiguration()
    {
        ApplyConfigFile();
        ApplyEnvironment();
        ApplyCommandLine();

        if (m_TargetPort <= 0 || m_TargetPort > 65535)
        {
            Debug.LogWarning($"[EyeTracker] invalid UDP port {m_TargetPort}, falling back to 15555");
            m_TargetPort = 15555;
        }
    }

    private void ApplyConfigFile()
    {
        var configPath = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "gaze_udp_config.json"));
        if (!File.Exists(configPath))
        {
            return;
        }

        try
        {
            var config = JsonUtility.FromJson<GazeUdpConfig>(File.ReadAllText(configPath));
            if (config == null)
            {
                return;
            }

            if (!string.IsNullOrWhiteSpace(config.target_host))
            {
                m_TargetHost = config.target_host.Trim();
            }

            if (config.target_port > 0)
            {
                m_TargetPort = config.target_port;
            }

            m_FlipViewportY = config.flip_viewport_y;
            Debug.Log($"[EyeTracker] loaded UDP config: {configPath}");
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"[EyeTracker] failed to load gaze_udp_config.json: {e.Message}");
        }
    }

    private void ApplyEnvironment()
    {
        var host = Environment.GetEnvironmentVariable("TOBII_GAZE_HOST");
        if (!string.IsNullOrWhiteSpace(host))
        {
            m_TargetHost = host.Trim();
        }

        var port = Environment.GetEnvironmentVariable("TOBII_GAZE_PORT");
        if (int.TryParse(port, out var parsedPort))
        {
            m_TargetPort = parsedPort;
        }

        var flipY = Environment.GetEnvironmentVariable("TOBII_GAZE_FLIP_Y");
        if (TryParseBool(flipY, out var parsedFlipY))
        {
            m_FlipViewportY = parsedFlipY;
        }
    }

    private void ApplyCommandLine()
    {
        var args = Environment.GetCommandLineArgs();
        for (var i = 0; i < args.Length; i++)
        {
            var arg = args[i];

            if (ReadStringArg(args, ref i, arg, "--gaze-host", out var host))
            {
                m_TargetHost = host;
                continue;
            }

            if (ReadIntArg(args, ref i, arg, "--gaze-port", out var port))
            {
                m_TargetPort = port;
                continue;
            }

            if (ReadBoolArg(args, ref i, arg, "--gaze-flip-y", out var flipY))
            {
                m_FlipViewportY = flipY;
                continue;
            }

            if (arg == "--gaze-no-flip-y")
            {
                m_FlipViewportY = false;
            }
        }
    }

    private static bool ReadStringArg(string[] args, ref int index, string arg, string name, out string value)
    {
        value = null;
        var prefix = name + "=";
        if (arg.StartsWith(prefix, StringComparison.Ordinal))
        {
            value = arg.Substring(prefix.Length).Trim();
            return !string.IsNullOrEmpty(value);
        }

        if (arg == name && index + 1 < args.Length)
        {
            value = args[++index].Trim();
            return !string.IsNullOrEmpty(value);
        }

        return false;
    }

    private static bool ReadIntArg(string[] args, ref int index, string arg, string name, out int value)
    {
        value = 0;
        if (ReadStringArg(args, ref index, arg, name, out var text))
        {
            return int.TryParse(text, out value);
        }

        return false;
    }

    private static bool ReadBoolArg(string[] args, ref int index, string arg, string name, out bool value)
    {
        value = false;
        if (ReadStringArg(args, ref index, arg, name, out var text))
        {
            return TryParseBool(text, out value);
        }

        return false;
    }

    private static bool TryParseBool(string text, out bool value)
    {
        value = false;
        if (string.IsNullOrWhiteSpace(text))
        {
            return false;
        }

        switch (text.Trim().ToLowerInvariant())
        {
            case "1":
            case "true":
            case "yes":
            case "on":
                value = true;
                return true;
            case "0":
            case "false":
            case "no":
            case "off":
                value = false;
                return true;
            default:
                return false;
        }
    }

    private static IPAddress ResolveAddress(string host)
    {
        if (IPAddress.TryParse(host, out var parsed))
        {
            return parsed;
        }

        var addresses = Dns.GetHostAddresses(host);
        foreach (var address in addresses)
        {
            if (address.AddressFamily == AddressFamily.InterNetwork)
            {
                return address;
            }
        }

        if (addresses.Length > 0)
        {
            return addresses[0];
        }

        throw new ArgumentException($"Unable to resolve host '{host}'");
    }

    private void SendFrame(
        float trackerTime,
        float unityTime,
        long trackerTimeUs,
        bool valid,
        float xNorm,
        float yNorm,
        float xPx,
        float yPx,
        float rawScreenX,
        float rawScreenY,
        float rawViewportX,
        float rawViewportY,
        int screenWidth,
        int screenHeight)
    {
        var sb = new StringBuilder(256);
        sb.Append("{\"t\":");
        AppendFloat(sb, trackerTime, 4);
        sb.Append(",\"unity_t\":");
        AppendFloat(sb, unityTime, 4);
        sb.Append(",\"tracker_us\":");
        sb.Append(trackerTimeUs.ToString(CultureInfo.InvariantCulture));
        sb.Append(",\"valid\":");
        sb.Append(valid ? "1" : "0");
        sb.Append(",\"x_norm\":");
        AppendFloat(sb, xNorm, 6);
        sb.Append(",\"y_norm\":");
        AppendFloat(sb, yNorm, 6);
        sb.Append(",\"x_px\":");
        AppendFloat(sb, xPx, 2);
        sb.Append(",\"y_px\":");
        AppendFloat(sb, yPx, 2);
        sb.Append(",\"sx\":");
        AppendFloat(sb, rawScreenX, 2);
        sb.Append(",\"sy\":");
        AppendFloat(sb, rawScreenY, 2);
        sb.Append(",\"vx\":");
        AppendFloat(sb, rawViewportX, 6);
        sb.Append(",\"vy\":");
        AppendFloat(sb, rawViewportY, 6);
        sb.Append(",\"screen_w\":");
        sb.Append(screenWidth);
        sb.Append(",\"screen_h\":");
        sb.Append(screenHeight);
        sb.Append("}");

        var data = Encoding.UTF8.GetBytes(sb.ToString());
        m_Client.Send(data, data.Length, m_EndPoint);
    }

    private static bool IsUnit(float value)
    {
        return IsFinite(value) && value >= 0.0f && value <= 1.0f;
    }

    private static bool IsFinite(float value)
    {
        return !float.IsNaN(value) && !float.IsInfinity(value);
    }

    private static void AppendFloat(StringBuilder sb, float value, int decimals)
    {
        if (float.IsNaN(value) || float.IsInfinity(value))
        {
            sb.Append("null");
            return;
        }

        sb.Append(value.ToString($"F{decimals}", CultureInfo.InvariantCulture));
    }
}
