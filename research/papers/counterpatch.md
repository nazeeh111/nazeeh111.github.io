# COUNTERPATCH: Exact Data-Repair Counterfactuals and a Negative Result for Added Search

Technical research report, 29 October 2026. Local reproducible artifact; not submitted or peer reviewed externally.

## Abstract

Training-data defect scores need not identify the best affordable repairs. We implement finite deletion and verified-label counterfactuals for fixed-feature ridge models, budgeted interaction-aware search, independent validation guards and conventional retraining. Two real public datasets support controlled training defects and independent writer/physical-condition shifts. A prospective source and target lock precedes 52 deletion and 24 post-audit label confirmation cells, producing 2040 before/after outcomes. The proposed beam selector fails its 10% two-task recovery target: it ties recomputed exact greedy on digits and improves Airfoil mean recovery by 1.4%, with a paired interval crossing zero. Label-quadratic optimization also ties greedy. A conventional full-data influence baseline recovers more mean error than the proposed constrained search. Transfer to random-forest regression degrades performance. 772 independent exhaustive real-data refits validate the algebra, while a separate runtime study shows the same greedy policy can use 2 rather than 166 model fits. The result is a working engineering tool and a verified negative selection result, not demonstrated algorithmic novelty or general reliability restoration.

## 1. Problem and prior art

Let a fixed training pipeline produce model `B(D)`. An action set `S` changes a derived dataset `D_S` at cost `c(S)`. We seek high independently measured repair utility under `c(S)≤b`, while observing cohort regressions. Detecting a defect, predicting a counterfactual and selecting a useful repair are different tasks. Label authenticity and annotation costs also remain separate from an optimizer's execution budget.

Downstream-oriented cleaning is established by [ActiveClean](https://www.vldb.org/pvldb/vol9/p948-krishnan.pdf), [BoostClean](https://arxiv.org/abs/1711.01299), and [COMET](https://www.openproceedings.org/2025/conf/edbt/paper-152.pdf). [CPClean](https://vldb.org/pvldb/vol14/p255-karlas.pdf) reasons about prediction certainty under missing-feature repairs. [Datascope](https://pages.cs.wisc.edu/~wentaowu/papers/iclr24-datascope.pdf) values data for pipeline utility and fairness. [Higher-order group influence](https://proceedings.mlr.press/v119/basu20b.html) and [MISS](https://arxiv.org/html/2409.18153v2) already challenge additive subset selection. [DATE-LM](https://arxiv.org/html/2507.09424v2) motivates evaluating retraining effects rather than retrieval rankings alone.

Recent [minimal-repair work](https://arxiv.org/html/2503.13921v2) concerns feature imputations and model certainty across remaining possible worlds, a different objective from selecting verified target edits using a labeled planning distribution. [Exact ridge cross-validation updates](https://arxiv.org/abs/2211.15128) and [ridge-head unlearning](https://arxiv.org/abs/2603.12977) establish the sufficient-statistic machinery we use. Neither exact updates, interaction terms, convex tangent bounds nor branch-and-bound are claimed as inventions. The experimental question is whether their particular constrained repair search earns its cost over serious conventional policies.

Portfolio inspection also found existing uncertainty-driven acquisition systems. Another generic surrogate optimizer would add little distinct evidence. We chose exact counterfactuals to make selection and numerical errors unusually inspectable. Source-level findings, recent literature and reproduction limits are retained in the [prior-art assessment](research-prior-art.md) and [independent alternatives](research-alternatives.md).

## 2. Supported objective and finite interventions

The supported model is

`B₀ = argmin_B ||XB−Y||²_F + λ||B||²_F`, with `λ>0`.

Features, preprocessing and the sum-loss penalty are fixed across interventions. Every column is penalized, including an explicit intercept. This matches sklearn Ridge with `fit_intercept=False`. Changing normalization after deletion, changing from sum to mean loss with an unchanged penalty, or retraining a feature extractor invalidates the contract.

Write `A=XᵀX+λI`, `R=Y−XB₀`. For deleted rows `S`,

`B₋S = B₀ − A⁻¹X_Sᵀ (I−X_S A⁻¹X_Sᵀ)⁻¹ R_S`.

The small block solve contains finite-deletion interactions. Dropping its correction yields a standard first-order deletion approximation; summing singleton utility loses interactions in the validation objective. Implementation uses Cholesky/linear solves, with explicit refusal when a downdate's absolute Schur scale or condition ratio is unsafe. All-row deletion is unsupported. “Exact” describes the finite mathematical identity; numerical agreement is separately tested against from-scratch fits.

For a preverified label delta `δ_i`, define planning prediction change `v_i=X_p A⁻¹x_i δ_i`. With `e=vec(Y_p−X_pB₀)` and columns `V_i=vec(v_i)`, exact planning MSE recovery is

`U(z) = aᵀz − zᵀQz`, where `a=2Vᵀe/m`, `Q=VᵀV/m`, and `m` counts planning target entries.

Here `Q` is positive semidefinite. A concave tangent upper-bounds `U` over binary selections. Maximizing its linear part under box and residual-budget constraints gives a fractional-knapsack upper bound for a branch. Numerical constrained optimization only supplies a tighter tangent point; its success flag never proves optimality. Best-first branch-and-bound retains a feasible incumbent, terminal uncertainty and remaining upper bound when a node/time limit stops it. Floating-point error allowances are reported; this is not an interval-arithmetic certificate or a population-risk bound. Safety constraints are checked separately on the chosen quadratic proposal, so its bound concerns the unconstrained candidate objective.

## 3. Selection and independent verification

Automatic deletion candidates are the 24 largest observed training residuals. Exact greedy recomputes finite bundle utility; beam keeps eight states per cost, and pair-lookahead considers pairs from a fixed 12-action screen. An additive ablation uses the same beam and exact group checks but replaces joint objective values with sums of singleton utilities. A no-planning-group ablation preserves the independent guard.

The search maximizes planning recovery within budget and planning-group harm limits, always allowing the empty action. One final proposal reaches a separate guard. It is executed only if average guard MSE does not worsen and no specified guard group exceeds tolerance; otherwise the workflow abstains without retry. The derived dataset is independently fit by sklearn Ridge from scratch. Evaluation labels never enter ranking, search or guard. A semantic replay checks input/derived bytes, actions, costs, group calculations, acceptance and both outcomes. It does not authenticate a manifest's author or verify the truth of caller-supplied annotations.

The engineering package exposes actual deletion and verified target edits through a CLI and numeric NPZ interface. All target candidates in the label study are audited before selection. Every method pays all 24 oracle queries, including correct labels and discarded candidates. Budget then means executed edits, not saved annotation effort. Automatic deletion uses no clean-label oracle; its budget means removed rows, not measured human review time.

## 4. Prospective experimental design

Original [UCI digits](https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits) train/test sources preserve the official writer separation. Training-only controlled flips map selected labels to `(class+1)%10`. Planning loss is one-hot score MSE; raw ridge scores are not probabilities, so this is not a Brier/calibration claim. We also report accuracy, macro recall and worst-class recall. Training-writer IDs within the source are unavailable, limiting independence among internal roles.

[NASA Airfoil measurements](https://archive.ics.uci.edu/dataset/291/airfoil+self+noise) support regression with controlled frequency-feature unit-like errors. Complete `(angle,chord,velocity,displacement)` condition groups stay together. The highest-velocity domain is held out; zero-corruption cases provide a real condition-shift setting without asserting natural annotation errors. Planning/guard groups are velocity strata; final groups are complete held-out conditions. MSE, RMSE, MAE and worst-condition errors are recorded.

Dirty-training-only scaling is frozen. Train, model-selection, planning, guard and development roles are separate; alpha 10 is fixed, leaving the model-selection role intentionally unused. Development seeds 0–2 select greedy as the product default before final outcomes. Original test writers and the maximum-velocity domain are not evaluated during development. Confirmation seeds 11–18, corruption 0/15/30%, and budgets 4/8 are locked in [the protocol](protocol-confirmation.md). Four additional quadratic-feature Airfoil cells remain the same ridge family.

The primary target requires beam to improve mean recovery at least 10% over exact greedy **on both tasks**, with a positive paired 95% seed-bootstrap lower bound. Rates 15/30% and budgets 4/8 are averaged within each seed first. At least 90% of proposed-method cells must avoid final MSE harm, with specified worst-group limits. Label optimization has a separate secondary target and cannot rescue a failed primary result. Targets were not weakened. Source/config/data/target hashes were locked before final evaluation; the original snapshot remains executable.

Every compatible comparator is retained: no repair, equal-budget random, loss, uncertainty, outliers, actual Cleanlab filtering/ranking with three-fold out-of-fold logistic probabilities, linear influence, exact singleton, KNN-Shapley, exact greedy, beam and ablations. KNN-Shapley uses the [Jia et al. PVLDB2019 recurrence](https://www.vldb.org/pvldb/vol12/p1610-jia.pdf), not the complete Datascope system. Full-data random/loss/influence and classification Cleanlab/Shapley avoid hiding the restricted search pool's weakness. Ranking policies use the common independent guard; planning-group constraints are an extra component of the proposed search, not an identical constraint imposed on every ranker.

DeMix source/checkpoint requirements and neural TRAK compatibility were investigated but not reproduced. DataPerf and nonmedical WILDS options were assessed; this is not their leaderboard protocol or a state-of-the-art comparison. Controlled public-data tasks establish a bounded local result.

## 5. Confirmation results

Recovery is `unrepaired final MSE − repaired final MSE`; larger is better. The table averages all corrupted primary rates and budgets, paired by the eight training/split seeds.

|Task|Greedy mean recovery|Beam mean recovery|Beam − greedy 95% interval|Relative extra recovery|Target|
|---|---:|---:|---:|---:|---|
|Digits score MSE|0.000158129|0.000158129|[0,0]|0%|Fail|
|Airfoil MSE, dB²|1.241507|1.258849|[−0.129535,0.181560]|1.40%|Fail|

Beam chooses identical accepted sets in 32/32 corrupted digit comparisons and 26/32 Airfoil comparisons. The additive ablation's Airfoil mean recovery is 1.334716, above joint beam's 1.258849; the proposed interaction mechanism therefore lacks an attributable independent advantage. Audited-label quadratic optimization matches greedy in 32/32 corrupted comparisons, with zero extra recovery and interval [0,0]. Its maximum reported numerical gap is 3.45e−10; all 24 small candidate references match exhaustive values. A tight planning bound does not create an outcome advantage.

Conventional full-data influence recovers mean 0.000257418 on digits and 1.559229 dB² on Airfoil, more than the constrained proposed search. It also avoids the 24-row residual screen, which is a plausible limitation of the proposed policy rather than evidence against all interaction reasoning. It is not a universal winner: removing planning constraints yields mean 1.65934 on Airfoil; exact singleton selection has a different harm profile; worst-class recall and compute rankings differ. A separate post-study generic-NPZ adapter exposes the conventional influence policy unchanged, with one guard and independent refits. It is an engineering usability addition, not a new confirmatory hypothesis.

At 15% corruption/budget 8, digit greedy reduces mean score MSE from 0.03848368 to 0.03830814 but changes mean accuracy by **−0.0139 percentage points**. Improving this surrogate has not established classification reliability restoration. Across all corrupted primary cells, full-data influence changes mean digit accuracy by +0.1774 percentage points, a modest observation rather than a broadly validated superiority claim. For Airfoil it changes mean RMSE from 6.7516 to 6.6368 dB.

The proposed method passes its aggregate risk thresholds but still harms 1/32 corrupted cells on each task. One accepted Airfoil plan increases final MSE by 1.844128 dB². Across all 1752 deletion outcomes, 585 guards reject proposals and 188 executed outcomes have negative final recovery. These counts include every comparator, control and feature-map cell. Validation protection is fallible under an unseen domain.

![Actual measured confirmation outcomes](../evidence/analysis-v2/repair-outcomes.png)

The first two panels illustrate the predeclared 15%/budget 8 stratum. The right panel normalizes each seed's beam-minus-greedy recovery by that task's mean greedy recovery, using both corrupted rates/budgets. [All strata](../evidence/analysis-v2/results.md) and [machine-readable statistics](../evidence/analysis-v2/summary.json) are retained. Intervals resample training/split/corruption seeds, while reusing fixed test writers and physical domains; they are not uncertainty across independent new domains. Model-selection multiplicity, small seed counts and narrow datasets limit inference.

## 6. Transfer, numerical validation and cost

The predeclared transfer design applies already selected actions to logistic classification or 80-tree random-forest regression on the first four seeds, budget 8, with no reselection. Exact native-model settings were implemented later, so this is not a fully source-locked native benchmark. On corrupted transfer settings, digit greedy/beam mean logistic MSE recovery is 0.000250086, with 1/8 harmful outcomes. Airfoil forest recovery is **−0.124916 for greedy and −0.333862 for beam**, with 3/8 and 5/8 harmful outcomes respectively. The ridge guard is not a forest guard. 132 actual native fits are saved. These failures rule out a broad cross-model reliability claim.

Independent real-data enumeration performs 772 conventional sklearn refits over all 386 subsets of a ten-candidate/budget 4 pool on each development task. Five selectors all reach the finite feasible planning optimum there. Maximum coefficient and planning-gain disagreements remain around 1e−13; numerical correctness does not imply selection novelty. In the full confirmation, maximum coefficient disagreement is 6.83e−13.

A separate fresh-cache, three-interleaving runtime study compares the **same greedy policy** using analytic evaluations or direct candidate refits. Every proposed/executed set and outcome matches in six paired comparisons. It uses two model fits versus 166, replacing 164 candidate refits with 165 analytic evaluations. Median complete measured cost is 0.417 s versus 2.265 s on digits and 0.091 s versus 0.802 s on Airfoil; beam adds overhead. Common setup, factorization, selection, guard and verification are included, but imports are excluded. Concurrent jobs and wide timing ranges make these descriptive measurements, not calibrated speed guarantees. Shared-cache confirmation per-method times are not speed evidence. The generic CLI additionally independently fits both baseline and repaired models after its analytic baseline solve.

The confirmation records 1928 model/detector fits for deletion and 312 fits for labels; summed suite time is 543.74 s under concurrent load. A separately installed core wheel runs actual synthetic deletion/label repair and replay outside the source tree, preserving original bytes and matching generating-source hashes. That consumer process peaks near 151 MB RSS; this is not a peak-memory measurement of every benchmark.

## 7. Independent attacks and reproducibility

Independent agent reviewers inspected raw code and artifacts. They found unsafe all-row selection, mutable verified targets/cache reports, tiny-Schur cancellation, semantic replay gaps, and a false zero-gap quadratic certificate caused by floating cancellation. Fixes retain the original failures. The quadratic repair passed 900 Decimal-based bound/solver checks across 90 problems, and the source package passes 60 tests covering numerical refits, exhaustive bounds, preservation, unsupported inputs, guard rejection and evaluation-label noninterference. Reviewers also recomputed the final statistics and identified the stronger influence baseline. This is independent agent scrutiny, not external human validation.

All raw results, source/data fingerprints, configs, failed development runs, numerical counterexamples, generated figures and reproduction commands are retained. Evidence is write-once by the program and checksum/semantic checked; it is not OS-immutable or externally authenticated. Source-specific limitations and every unsupported pipeline transformation are explicit. See [reproduction](reproducibility.md), [review](final-independent-review.md) and [usage](usage.md).

## 8. Contribution status and stopping decision

Achievement level 1 is demonstrated: supported real models/data undergo proposed repairs, derived-data execution, fresh retraining and independent outcome measurement. Level 2, a reproducible repair-quality/cost/risk advantage over serious competition, is **not demonstrated**. Level 3, a novel publishable contribution, is **not established**. Exact ridge identities and standard optimization are prior art; original implementation and engineering integration do not change that.

The useful finished alternative includes exact greedy and a stronger observed conventional full-data influence policy. The evidence supports narrow computational engineering and a negative result for added search in this protocol. It does not establish genuine causal diagnosis, optimal annotation acquisition, globally minimal repair over the whole dataset, population safety, arbitrary-model support or external adoption. We stop this hypothesis rather than retuning against the final domains. Future work would need new development data and a fresh lock, especially for candidate generation, stateful costed label acquisition and model-specific guard transfer.
