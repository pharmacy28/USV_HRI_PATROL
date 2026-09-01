// ============================================================================
#nullable disable
// coverage_field.cs — 覆盖场: 栅格 + 检测模型 + 贝叶斯信念 + 指标 (无 Unity 依赖提炼版)
//
// 源文件: Assets/Scripts/Planning/PlannerPathPlanningService.cs #region CoverageField (24–315 行)
// 文档:   ../docs/01_belief_and_coverage_field.md
//
// 提炼差异: Mathf → MathF; Debug.Log → 移除; 配置读取精简为 ProbabilityModelConfig。
// 算法语义逐段一致, 详见 ../source_map.md
// ============================================================================

using System;
using System.Collections.Generic;

namespace UsvPatrolPlanning
{
    /// <summary>覆盖场: 内存栅格, 零 I/O。规划器的感知基础。</summary>
    public class CoverageField
    {
        // ── 网格状态 ──
        private int _gridColumns, _gridRows, _gridCellSize = 50;
        private float _gridOriginX, _gridOriginY;
        private float[] _pmiss, _belief;
        private bool[] _obstacleMask;
        private bool _gridInitialized;

        // ── 传感器/衰减参数 ──
        private float _timeDecayPerHour;
        private string _timeDecayMode = "none";
        private float _pmissRecoveryBoost = 1f;
        private int _obstacleInflationRadius = 80;
        private readonly Dictionary<int, DetectorFormulaConfig> _detectorFormulas = new Dictionary<int, DetectorFormulaConfig>();

        // ── 派生指标 ──
        private int _freeCellCount;
        private float _meanPmiss = 1f, _c80, _totalRisk = 1f;
        private bool _statsDirty = true;
        private double _elapsedSeconds;

        public int Columns => _gridColumns;
        public int Rows => _gridRows;
        public int CellSize => _gridCellSize;
        public float OriginX => _gridOriginX;
        public float OriginY => _gridOriginY;
        public bool Initialized => _gridInitialized;
        public float[] Pmiss => _pmiss;
        public float[] Belief => _belief;
        public bool[] ObstacleMask => _obstacleMask;
        public double ElapsedSeconds => _elapsedSeconds;

        // ═══ 初始化 (源 76–140 行) ═══

        public void ApplyProbabilityModelConfig(ProbabilityModelConfig pm)
        {
            if (pm == null) return;
            _gridCellSize = Math.Max(20, pm.GridCellSize);
            _obstacleInflationRadius = Math.Max(20, pm.ObstacleInflationRadius);
            _timeDecayMode = string.IsNullOrWhiteSpace(pm.TimeDecayMode) ? "none" : pm.TimeDecayMode.Trim().ToLowerInvariant();
            _timeDecayPerHour = Math.Max(0f, pm.TimeDecayPerHour);
            _pmissRecoveryBoost = Math.Max(0f, pm.PmissRecoveryBoostForDemo);
            _detectorFormulas.Clear();
            if (pm.DetectorFormulas != null)
                foreach (var d in pm.DetectorFormulas)
                    if (d != null) _detectorFormulas[d.ScanType] = d;
        }

        public void Initialize(PlannerParam param, List<ShipDes> ships = null)
        {
            if (param.Width <= 0 || param.Height <= 0) return;
            _gridOriginX = param.X;
            _gridOriginY = param.Y;
            _gridColumns = Math.Max(1, (int)MathF.Ceiling((float)param.Width / _gridCellSize));
            _gridRows = Math.Max(1, (int)MathF.Ceiling((float)param.Height / _gridCellSize));
            int n = _gridColumns * _gridRows;
            _pmiss = new float[n];
            _belief = new float[n];
            _obstacleMask = new bool[n];
            for (int i = 0; i < n; i++) _pmiss[i] = 1f;
            MarkObstacles(param.ObcRects);
            _freeCellCount = 0;
            for (int i = 0; i < n; i++) if (!_obstacleMask[i]) _freeCellCount++;
            float ub = _freeCellCount > 0 ? 1f / _freeCellCount : 0f;
            for (int i = 0; i < n; i++) _belief[i] = _obstacleMask[i] ? 0f : ub;
            _gridInitialized = true;
            _statsDirty = true;
            _elapsedSeconds = 0;
        }

        // ═══ 障碍物 (源 142–195 行) ═══

        /// <summary>ObcRect → 圆形障碍 (与航路点过滤 IsWaypointInsideObstacle 语义一致)</summary>
        public static (float cx, float cz, float radius) ObcRectToCircle(ObcRect o)
            => (o.X + o.Width * 0.5f, o.Y + o.Height * 0.5f, MathF.Max(o.Width, o.Height) * 0.5f);

        public void MarkObstacles(List<ObcRect> obs)
        {
            if (obs == null || obs.Count == 0) return;
            int n = _gridColumns * _gridRows;
            float inflation = _obstacleInflationRadius;
            for (int i = 0; i < obs.Count; i++)
            {
                var o = obs[i];
                var (ocx, ocz, oradius) = ObcRectToCircle(o);
                float finalR = oradius + inflation;
                float r2 = finalR * finalR;

                int colMin = Math.Max(0, (int)MathF.Floor((ocx - finalR - _gridOriginX) / _gridCellSize));
                int colMax = Math.Min(_gridColumns - 1, (int)MathF.Ceiling((ocx + finalR - _gridOriginX) / _gridCellSize));
                int rowMin = Math.Max(0, (int)MathF.Floor((ocz - finalR - _gridOriginY) / _gridCellSize));
                int rowMax = Math.Min(_gridRows - 1, (int)MathF.Ceiling((ocz + finalR - _gridOriginY) / _gridCellSize));

                for (int r = rowMin; r <= rowMax; r++)
                    for (int c = colMin; c <= colMax; c++)
                    {
                        int idx = r * _gridColumns + c;
                        if (idx >= n || _obstacleMask[idx]) continue;
                        float cx = ColToWorldX(c), cz = RowToWorldZ(r);
                        float dx = cx - ocx, dz = cz - ocz;
                        if (dx * dx + dz * dz <= r2) _obstacleMask[idx] = true;
                    }
            }
        }

        /// <summary>运行时更新障碍物 mask (源 184–195 行)</summary>
        public void ApplyObstacles(List<ObcRect> obs)
        {
            if (!_gridInitialized || obs == null) return;
            int n = _gridColumns * _gridRows;
            for (int i = 0; i < n; i++) _obstacleMask[i] = false;
            MarkObstacles(obs);
            _freeCellCount = 0;
            for (int i = 0; i < n; i++) if (!_obstacleMask[i]) _freeCellCount++;
            RecomputeBelief();
            _statsDirty = true;
        }

        // ═══ 传感器扫描 + 信念 (源 201–283 行) ═══

        public void UpdateSearchProbabilities(double dt, List<ShipDes> ships)
        {
            if (!_gridInitialized || ships == null || ships.Count == 0) return;
            float dts = MathF.Max(0.001f, (float)dt);
            int n = _gridColumns * _gridRows;
            for (int si = 0; si < ships.Count; si++)
            {
                var s = ships[si];
                if (s.ScanMethods == null || s.ScanMethods.Count == 0) continue;
                float mr = 0f;
                for (int mi = 0; mi < s.ScanMethods.Count; mi++)
                    if (s.ScanMethods[mi].VisionRange > mr) mr = s.ScanMethods[mi].VisionRange;
                if (mr <= 0f) continue;
                int rc = (int)MathF.Ceiling(mr / _gridCellSize) + 1;
                int sc = WorldToCol(s.X), sr = WorldToRow(s.Y);
                int c0 = Math.Max(0, sc - rc), c1 = Math.Min(_gridColumns - 1, sc + rc);
                int r0 = Math.Max(0, sr - rc), r1 = Math.Min(_gridRows - 1, sr + rc);
                for (int r = r0; r <= r1; r++)
                    for (int c = c0; c <= c1; c++)
                    {
                        int idx = r * _gridColumns + c;
                        if (idx >= n || _obstacleMask[idx]) continue;
                        float cx = ColToWorldX(c), cz = RowToWorldZ(r);
                        float dist = MathF.Sqrt((cx - s.X) * (cx - s.X) + (cz - s.Y) * (cz - s.Y));
                        float pmc = 1f; bool any = false;
                        for (int mi = 0; mi < s.ScanMethods.Count; mi++)
                        {
                            var m = s.ScanMethods[mi];
                            if (m.ScanType <= 0 || m.VisionRange <= 0) continue;
                            if (dist <= m.VisionRange)
                            { any = true; pmc *= 1f - ComputePDetect(m, dist); }
                        }
                        if (any) _pmiss[idx] *= Clamp01(pmc);
                    }
            }
            ApplyTimeDecay(dts);
            RecomputeBelief();
            _statsDirty = true;
            _elapsedSeconds += dts;
        }

        /// <summary>检测概率距离曲线 (源 242–262 行)</summary>
        private float ComputePDetect(ScanMethod m, float dist)
        {
            if (m.SearchProb <= 0f) return 0f;
            float t = Clamp01(dist / Math.Max(1, m.VisionRange));
            if (!_detectorFormulas.TryGetValue(m.ScanType, out var d))
                return m.SearchProb * (0.18f + 0.82f * (1f - MathF.Pow(t, 1.35f)));
            float f = EvalCurve(d, t);
            return Clamp01(m.SearchProb * d.Gain * (d.EdgeProbabilityFactor + (1f - d.EdgeProbabilityFactor) * f));
        }

        private static float EvalCurve(DetectorFormulaConfig d, float t)
        {
            switch ((d.DistanceCurve ?? "power").Trim().ToLowerInvariant())
            {
                case "flat": return 1f;
                case "linear": return 1f - t;
                case "exponential":
                    float l = Math.Max(0.01f, d.ExponentialLambda);
                    return Math.Max(0f, (MathF.Exp(-l * t) - MathF.Exp(-l)) / (1f - MathF.Exp(-l)));
                default: return 1f - MathF.Pow(t, Math.Max(0.1f, d.Exponent));
            }
        }

        private void ApplyTimeDecay(float dt)
        {
            if (_timeDecayPerHour <= 0f || _pmissRecoveryBoost <= 0f) return;
            float h = dt / 3600f, gamma;
            switch (_timeDecayMode)
            {
                case "exponential":
                case "recovery_exponential": gamma = 1f - MathF.Exp(-_timeDecayPerHour * h); break;
                case "linear":
                case "recovery_linear": gamma = Math.Min(1f, _timeDecayPerHour * h); break;
                default: return;
            }
            float b = _pmissRecoveryBoost * gamma;
            int n = _gridColumns * _gridRows;
            for (int i = 0; i < n; i++) if (!_obstacleMask[i]) _pmiss[i] = Clamp01(_pmiss[i] + (1f - _pmiss[i]) * b);
        }

        /// <summary>贝叶斯信念归一化: belief[i] = Pmiss[i] / Σ Pmiss</summary>
        public void RecomputeBelief()
        {
            int n = _gridColumns * _gridRows; float sum = 0f;
            for (int i = 0; i < n; i++) if (!_obstacleMask[i]) sum += _pmiss[i];
            float inv = sum > 0f ? 1f / sum : 0f;
            for (int i = 0; i < n; i++) _belief[i] = _obstacleMask[i] ? 0f : _pmiss[i] * inv;
        }

        // ═══ 指标 (源 289–313 行) ═══

        private void RefreshStats()
        {
            if (!_statsDirty) return; _statsDirty = false;
            int n = _gridColumns * _gridRows;
            float psum = 0f, rsum = 0f; int covered = 0, free = 0;
            for (int i = 0; i < n; i++)
            {
                if (_obstacleMask[i]) continue;
                free++;
                float p = _pmiss[i];
                psum += p;
                rsum += p * _belief[i];
                if (1f - p > 0.8f) covered++;    // C80 硬编码阈值 0.8
            }
            _freeCellCount = free;
            _meanPmiss = free > 0 ? psum / free : 1f;
            _c80 = free > 0 ? (float)covered / free : 0f;
            _totalRisk = rsum;
        }

        public float GetCoverageTotalRisk() { RefreshStats(); return _totalRisk; }
        public float GetC80() { RefreshStats(); return _c80; }
        public float GetMeanCoverage() { RefreshStats(); return 1f - _meanPmiss; }
        public float GetMeanPmiss() { RefreshStats(); return _meanPmiss; }
        public int FreeCellCount { get { RefreshStats(); return _freeCellCount; } }

        // ═══ 坐标转换 (源 1323–1326 行) ═══

        public int WorldToCol(float wx) => Math.Clamp((int)MathF.Floor((wx - _gridOriginX) / _gridCellSize), 0, _gridColumns - 1);
        public int WorldToRow(float wz) => Math.Clamp((int)MathF.Floor((wz - _gridOriginY) / _gridCellSize), 0, _gridRows - 1);
        public float ColToWorldX(int col) => _gridOriginX + (col + 0.5f) * _gridCellSize;
        public float RowToWorldZ(int row) => _gridOriginY + (row + 0.5f) * _gridCellSize;

        /// <summary>环形搜索最近自由格 (源 1328–1347 行)</summary>
        public (int idx, int col, int row, float wx, float wz) FindNearestFreeCell(float wx, float wz)
        {
            int bc = WorldToCol(wx), br = WorldToRow(wz);
            for (int r = 0; r < _gridRows; r++)
                for (int d = 0; d <= Math.Max(_gridColumns, _gridRows); d++)
                    for (int dc = -d; dc <= d; dc++)
                    {
                        int c = bc + dc, row = br + (d - Math.Abs(dc));
                        if (c >= 0 && c < _gridColumns && row >= 0 && row < _gridRows)
                        {
                            int idx = row * _gridColumns + c;
                            if (!_obstacleMask[idx]) return (idx, c, row, ColToWorldX(c), RowToWorldZ(row));
                        }
                        row = br - (d - Math.Abs(dc));
                        if (row >= 0 && row < _gridRows && row != br + (d - Math.Abs(dc)))
                        {
                            int idx = row * _gridColumns + c;
                            if (!_obstacleMask[idx]) return (idx, c, row, ColToWorldX(c), RowToWorldZ(row));
                        }
                    }
            return (-1, bc, br, ColToWorldX(bc), RowToWorldZ(br));
        }

        private static float Clamp01(float v) => v < 0f ? 0f : (v > 1f ? 1f : v);
    }
}
