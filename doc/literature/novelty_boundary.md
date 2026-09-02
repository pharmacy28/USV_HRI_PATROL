# Innovation Boundary v2 — after the second literature pressure test

## 1. Primary contribution candidate

### Predictive fleet-level responsibility reconfiguration under dynamic human takeover

The contribution is **not**:
- predicting a human trajectory;
- predicting a future human search region;
- avoiding future overlap;
- freezing a center;
- using Bayesian belief;
- using Lloyd/K-means, A*, or Hungarian.

The current defensible kernel is:

1. A member of the **same probabilistic-search robot fleet** changes from autonomous operation to human control during the mission.
2. The system estimates a fixed-horizon future state
   \[
   \hat p_h(t+H).
   \]
3. The forecast is interpreted as **prospective search responsibility**, not as target evidence and not as a hard-cleared region.
4. It is represented as an explicit fixed planning generator/anchor during one responsibility solve.
5. **All searchable free cells remain in the problem**, while only autonomous generators are updated.
6. The resulting fleet-wide responsibility structure is regenerated before path generation and assignment.
7. Human prediction never changes
   \[
   b_i^t=P(X=x_i\mid Z_{1:t})
   \]
   unless an independently calibrated probabilistic human-observation model is introduced.

A concise candidate statement is:

> We study predictive responsibility reconfiguration under dynamic human takeover of a member of the same probabilistic-search fleet. A fixed-horizon forecast of the human-controlled vehicle is represented as prospective search responsibility during full-domain posterior-weighted repartitioning, while target belief remains conditioned on sensing evidence.

## 2. Why this still differs from the closest literature

- **Xie et al. 2011:** predicts a human's next search location and inhibits robot search there. Our question is whether a predicted human-controlled fleet member should become a generator of the *team's responsibility geometry*, without treating the predicted region as cleared.
- **Heintzman et al. 2021:** anticipates independent ground-searcher paths and optimizes UAV trajectories. Our human is dynamically controlling a member of the same robot fleet, and the predicted state changes an explicit responsibility layer.
- **Krzysiak & Butail 2022/2025:** human teleoperates a reference robot and autonomous teammates adapt search/assistance based on movement and inferred human knowledge. Their control blends follow/assist versus independent search; ours explicitly regenerates a multi-robot responsibility partition.
- **Ishii et al. 2023:** predicts future human search regions to reduce duplication. The human is an independent searcher and the method does not address a robot fleet whose autonomy composition changes through takeover.
- **Talebpour & Martinoli:** future human motion affects risk-aware bids/replanning for predefined tasks. Ours changes the upstream set/geometry of search responsibilities.
- **Cortés/Fu:** establish weighted spatial partition and current-position task regions; neither provides the human-takeover/prospective-responsibility semantics.

## 3. Second contribution candidate

### Empirically validated perception-to-search probabilistic interface

A strong version requires actual experiments, not just equations:

\[
(d,\beta)
\rightarrow
P_D(d,\beta)
\rightarrow
\nu_{\rm eff}
\rightarrow
h(d,\beta)
\rightarrow
\Delta\Lambda_i
\rightarrow
b_i^t,\;R_{\rm miss}(t).
\]

Required validation layers:
1. Sensor-level calibration: predicted \(P_D\) versus held-out detection rates.
2. Temporal calibration: native video correlation and first-effective-detection waiting-time adequacy.
3. Mission-level calibration: predicted \(R_{\rm miss}(t)\) versus held-out empirical nondetection frequency.
4. Planner performance remains evaluated with actual \(T_{\rm FD}\), detection probability before budget, KM/RMST, failures, and redundancy.

If the simulator simply samples detections from the same fitted \(P_D\) used to compute \(R_{\rm miss}\), the mission-level “validation” is circular and does not support this contribution.

## 4. New experimental questions produced by the literature review

### A. Mechanism versus direct inhibition
Add an **Xie-inspired Predictive Inhibition** baseline:
- predictor is identical to H3;
- predicted human region modifies planning preference / inhibition only;
- target posterior is untouched;
- compare against prospective-anchor global repartition.

This tests whether the contribution is more than “predict where the human goes and avoid it.”

### B. Human miss robustness
Because \(P_D<1\), the human-controlled USV can visit a predicted region and still miss the target.
Test whether hard/direct inhibition creates brittle under-search, whereas full-domain repartition retains residual responsibility after real negative evidence.

### C. Responsibility mediation
Do not stop at FDE:
\[
\mathrm{FDE}
\rightarrow
E_{\rm responsibility}
\rightarrow
E_{\rm redundant\ sensing}
\rightarrow
T_{\rm FD}.
\]
A useful paper should demonstrate this causal/mechanistic chain rather than only correlate predictor accuracy with mission time.

### D. Conflict-opportunity stratification
Predeclare low/medium/high **prospective human–autonomy conflict opportunity** scenarios.
The H3–H2 benefit should be interpreted in relation to how much opportunity exists for future spatial duplication.

### E. Fleet-size effect
Test the coordination effect, not only runtime:
\[
R_A\in\{1,3,5,9\}
\]
or another defensible set. Benefit may increase, decrease, or be non-monotonic; do not assume the direction.

### F. Planner dependence
Where feasible, compare the predictive mechanism on:
- the transparent posterior-weighted geometric responsibility planner;
- a short-horizon sensor-aware expected-detection benchmark
\[
U_{\rm det}(\mathcal P)=\sum_i b_i^t\left(1-e^{-\Delta\Lambda_i(\mathcal P)}\right).
\]
This tests whether H3 is merely an artifact of one Lloyd/K-means-like substrate.

## 5. Reviewer-facing risks still unresolved

- Is a single point \(\hat p_h(t+H)\) sufficient versus a full probabilistic trajectory/occupancy tube?
- How is prediction horizon \(H\) selected without using final mission results?
- What exact responsibility-error metric is used?
- What is the exact detector likelihood/false-positive confirmation model?
- Is full-domain geometric repartition still defensible with directional sensing and obstacles?
- Does the approach remain useful when the fleet is large?
- Does replay-based causal evidence survive a smaller live closed-loop HRI validation?
