# 单静止目标搜索：多 WAM-V 传感器融合与路径规划框架

> 本文整理 2026-08-05 的头脑风暴，作为论文建模和工程实现的共同基线。假设：搜索区域已栅格化、目标只有一个、目标静止；WAM-V 可以运动，传感器观测随时间变化。

## 1. 先固定建模边界

### 1.1 单目标假设

目标位置假设为离散随机变量：

\[
H\in\{1,2,\ldots,N\},
\]

其中 (H=c) 表示目标位于格栅 (c)。每个时刻维护：

- (b_c=P(H=c\mid\mathcal{Y}_{1:t}))：目标存在信念；
- (m_c)：若目标确实位于 (c)，在已有探测机会下仍未被人机确认的累计漏检概率；
- (w_c)：贝叶斯更新使用的未归一化权重。

初始化为：

\[
w_c^{(0)}=b_c^{(0)}=\pi_c,\qquad m_c^{(0)}=1.
\]

所有格栅信念归一化：

\[
b_c=\frac{w_c}{\sum_k w_k}.
\]

> 该全局归一化只适用于单目标。若以后恢复多个目标，必须改成每个目标一张信念图或独立占据概率模型，不能把所有目标压成一张总和为 1 的图。

### 1.2 当前工程约束

当前 VRX 摄像头是单目 RGB（1280×720、约 80° 水平视场、30 Hz），代码中 `selected_camera_relay` 主要服务于操作员查看选中艇的视频。真正搜索时必须订阅每艘 WAM-V 的原始相机数据，而不能只处理 `selected_camera`。

## 2. 每艘 WAM-V 的观测输入

每艘艇 (i) 的检测节点输出一条结构化观测：

```json
{
  "wamv": "wamv_01",
  "stamp": 123.4,
  "candidates": [
    {"u": 640, "v": 360, "width": 42, "height": 28, "score": 0.82}
  ],
  "image_quality": 0.76
}
```

必须保留候选框位置；只有“整帧报警/不报警”而没有候选框，无法有效区分视场内的不同格栅。

原始订阅主题按艇编号为：

```text
/wamv_01/sensors/cameras/front_camera_sensor/image_raw
/wamv_02/sensors/cameras/front_camera_sensor/image_raw
...
```

建议每 0.5–1 s 使用每艘艇的最新帧做一次融合，而不是把 30 Hz 的相邻帧当作 30 次独立观测。

## 3. 从格栅假设到图像几何

对每艘艇 (i) 和格栅 (c)：

1. 从 WAM-V 位姿、摄像头外参和 `CameraInfo.K` 得到世界坐标到光学坐标的变换；
2. 将格栅中心投影到图像：

\[
u=f_xX/Z+c_x,\qquad v=f_yY/Z+c_y;
\]

3. 计算假设距离：

\[
r_{i,c}=\|p_c-p_i\|;
\]

4. 检查 (Z>0)、是否落在图像范围、是否超过最大探测距离、是否被已知障碍遮挡；
5. 计算目标假设投影尺寸，例如已知目标有效高度 (H_t) 时：

\[
h_{i,c}^{\text{exp}}\approx f_yH_t/r_{i,c}.
\]

这里不要求 RGB 摄像头直接测出真实距离。对每个候选格栅分别假设“目标在这里”，即可使用该格栅的几何距离计算对应的传感器似然。

定义可见性 (V_{i,c}\in\{0,1\})。若 (V_{i,c}=0)，该艇对该格栅本次没有直接观测信息。

## 4. 摄像头探测模型

对可见格栅建立：

\[
P_D^{i,c}=P(A_i=1\mid H=c),
\]

\[
P_{FA}^{i,c}=P(A_i=1\mid H\ne c),
\]

其中 (A_i) 表示“在格栅 (c) 的投影邻域出现匹配报警”。第一版可以使用距离、检测器分数、目标预计像素尺寸和图像质量：

\[
P_D^{i,c}=V_{i,c}\,\sigma(\beta_0+\beta_1\log(r_{i,c}+1)+\beta_2s_{i,c}+\beta_3q_i).
\]

参数通过仿真标定获得。对距离区间 (r_k)，用带平滑的频率估计：

\[
\hat P_D(r_k)=\frac{n_{hit}(r_k)+1}{n_{target}(r_k)+2},\qquad
\hat P_{FA}(r_k)=\frac{n_{false}(r_k)+1}{n_{negative}(r_k)+2}.
\]

仿真数据记录至少包含：时间、WAM-V、目标真值位置、真值距离、候选框、检测分数、图像质量、是否报警。运行时不读取 Gazebo 真值；真值只用于离线标定和评估。

## 5. 用图像观测更新信念格栅

将检测框与格栅投影位置匹配。匹配可以使用像素距离、检测框膨胀后的包含关系和预计目标尺寸。

若匹配报警：

\[
\Lambda_{i,c}(1)=\frac{P_D^{i,c}}{P_{FA}^{i,c}}.
\]

若可见但没有匹配报警：

\[
\Lambda_{i,c}(0)=\frac{1-P_D^{i,c}}{1-P_{FA}^{i,c}}.
\]

随后：

\[
w_c\leftarrow w_c\Lambda_{i,c}(A_i).
\]

将同一融合周期内的所有 WAM-V 观测依次处理后，再统一归一化：

\[
b_c=\frac{w_c}{\sum_k w_k}.
\]

超出探测范围或不可见时令 (Λ_{i,c}=1)，因此不直接改变该格栅；其他格栅更新后，全局归一化仍会间接改变它的信念。

概率必须限制在 ([10^{-4},1-10^{-4}])，避免零概率导致某格栅永久消失。

## 6. 漏检率更新

机器报警后由操作员二分确认。设操作员在真实目标存在时正确确认的概率为 (s_H)，则一次完整人机确认的有效探测概率为：

\[
P_{D,eff}^{i,c}=P_D^{i,c}s_H.
\]

每个独立探测机会更新：

\[
m_c\leftarrow m_c(1-P_{D,eff}^{i,c}).
\]

若暂时不考虑操作员，取 (s_H=1)。不可见或超量程时 (P_D=0)，所以 (m_c) 不更新。

多个 WAM-V 的观测只有在近似条件独立时才能直接连乘。视场高度重叠时使用相关性折扣 (alpha_i\in(0,1])：

\[
m_c\leftarrow m_c(1-\alpha_iP_D^{i,c}s_H).
\]

信念 (b_c) 要归一化，漏检率 (m_c) 不归一化；两者不能混成一个变量。

任务级剩余漏检风险定义为：

\[
R_{miss}=\sum_c b_cm_c.
\]

它是当前信念加权的工程风险指标。任务可以在人工确认目标，或 (R_{miss}<\epsilon_{miss})，或达到时间/燃料上限时结束。

## 7. 人机确认的二次更新

机器报警后显示候选图像、位置、机器概率和估计距离，操作员只选择：

```text
[确认] [否定]
```

若确认，任务可直接终止；若继续维护后验，则使用人工似然比：

确认：

\[
\Lambda_H(1)=\frac{s_H}{f_H};
\]

否定：

\[
\Lambda_H(0)=\frac{1-s_H}{1-f_H},
\]

其中 (f_H) 是目标不存在时误确认的概率。操作员没有被请求确认时，不加入人工似然。

## 8. 实际程序结构

建议拆成四个节点：

```text
fleet_camera_detector
    └── 输出每艘艇的候选框、分数和图像质量

grid_observation_model
    └── 根据位姿、CameraInfo 和格栅坐标计算可见性、距离、PD、PFA

belief_update_node
    └── 更新 w[c]、b[c]、pmiss[c]、Rmiss

operator_console
    └── 显示候选并发布确认/否定
```

第一版可以用 `std_msgs/String` 传 JSON，稳定后再定义专用 ROS 消息。建议输出：

```text
/hri/detections/wamv_01
/hri/detections/wamv_02
...
/hri/grid_belief
/hri/operator_verdict
```

核心融合伪代码：

```python
for wamv in all_wamvs:
    obs = latest_observation[wamv]
    pose = latest_pose[wamv]

    for cell in grid:
        proj = project_cell(pose, cell)
        if not proj.visible:
            continue

        pd = pd_model(proj.range, proj.expected_size, obs.quality)
        pfa = pfa_model(proj.range, obs.quality)
        matched = match_candidate(proj.pixel, obs.candidates)

        if matched:
            likelihood = pd / pfa
        else:
            likelihood = (1.0 - pd) / (1.0 - pfa)

        w[cell] *= likelihood
        pmiss[cell] *= 1.0 - pd * human_sensitivity

normalize_belief(w, b)
Rmiss = sum(b[c] * pmiss[c] for c in grid)
```

## 9. 与路径规划连接

在每个重规划周期，用当前格栅状态计算搜索价值：

\[
U_c=b_cm_cP_D^{next}(c).
\]

高 (U_c) 表示：目标在这里的可能性高、目前仍可能漏检、下一次前往有较大探测收益。

随后执行：

```text
U[c] 计算
→ 高价值格栅聚类
→ 计算 WAM-V 到聚类的航行代价
→ 匈牙利算法分配 WAM-V
→ 为每艘艇选择可观察视点
→ A* 规划到视点的无碰撞路径
→ 执行一小段
→ 重新融合所有传感器
```

A* 的目标不应只是格栅中心，而应是能够让目标格栅进入摄像头视场的观察点。

## 10. 必须避免的逻辑错误

1. 只处理 `selected_camera`，而不处理所有 WAM-V 的传感器；
2. 把漏检率 (m_c) 和目标信念 (b_c) 一起归一化；
3. 每一帧都当作独立观测，导致概率虚假收敛；
4. 使用 Gazebo 真值距离作为运行时传感器输入；
5. 只有整帧报警而没有候选位置，却声称完成了精确格栅更新；
6. 在目标已经确认后继续把同一观测累积到搜索风险中；
7. 忽略多艇视场重叠造成的观测相关性。

这套单目标、静止目标模型先作为论文和代码的基本框架。完成传感器标定和格栅更新后，再接入聚类、匈牙利指派和 A*，避免在传感器数学模型尚未确定时提前固化路径规划逻辑。
