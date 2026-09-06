# Astra announcement event study design version 1

Recorded 2026-09-06 before inspecting sample-company event returns. This is a retrospective analysis plan, not a public preregistration and not evidence that the researcher was unaware of the event. A broad-market SPY data-availability probe preceded this record; no sample-company outcome was inspected.

## Research question
How did listed firms at different positions in the AI value chain reprice around OpenAI's September 3 2026 Astra announcement? The proposed mechanism distinguishes computing infrastructure, business workflow software and cybersecurity. Capability and deployment safeguards are jointly announced; neither is separately identified by this event.

## Scope and fixed sample
Purposive illustrative US-traded sample, eight firms per portfolio; not a census or representative sample. Groups describe business models and are imperfect proxies for exposure; they are not validated firm-level mechanism measures.

Infrastructure: NVDA AMD AVGO MU ARM MRVL ANET DELL.
Workflow software: ADBE CRM NOW WDAY TEAM HUBS INTU PATH.
Cybersecurity: CRWD PANW FTNT ZS OKTA S TENB QLYS.
Benchmarks: SPY (primary), QQQ (sensitivity), XLK (secondary sensitivity).

No replacement based on returns. Missing or insufficient observations are reported with reasons. Require at least 200 of 220 estimation-session observations and every event-session return; no forward filling. Balanced complete-case group portfolios are equal weighted and rebalanced daily. Minimum six available firms per group for headline group comparisons.

## Event and data horizon
Calendar event date 2026-09-03. Data cutoff 2026-09-04 US close; today 2026-09-06. Only sessions 0 and 1 are observable. Longer windows are unavailable, not zero. US Labor Day 2026-09-07 is closed. Announcement intraday minute remains unverified; daily results describe the announcement day and surrounding information environment. Official Aug 7, Aug 18 and Sep 1 Astra communications indicate anticipation. Sep 4 payrolls, Sep 1 rival model and Sep 2 rival model announcements, and corporate earnings are confounders.

## Outcomes and model
Daily simple total-return proxy from publicly accessible adjusted closing prices; archive provider payloads, retrieval time, and SHA-256. Publicly accessible does not imply unrestricted redistribution. Daily return = adjusted close[t] / adjusted close[t-1] - 1. Primary market model R[p,t] = alpha[p] + beta[p] R[SPY,t] + error[p,t], estimated on event sessions [-250,-31], 220 sessions before missingness. Use SPY trading calendar. Fit portfolios directly to preserve within-date cross-firm dependence. CAR is the sum of abnormal simple returns, not a compounded holding-period return.

Primary window [0,0], because day 1 contains payroll news and additional earnings. Primary two-sided tests: infrastructure-minus-workflow CAR; cybersecurity-minus-workflow CAR. Holm adjustment across these two tests. Report effect sizes, forecast-error standard errors (including coefficient-estimation uncertainty), t reference p values with estimation residual degrees of freedom, and 95% confidence intervals. Inference is conditional on the expected-return model, stable error variance and no omitted simultaneous portfolio news; does not establish causality.

Secondary descriptive windows [-1,0], [0,1], [-2,1], and [-5,-1]. No confirmatory significance claims for these windows. Report raw returns, firm abnormal returns and group abnormal paths [-10,+1]. Market-adjusted returns, QQQ and XLK models, leave-one-company-out spread ranges, and documented earnings exclusions are sensitivity checks, not alternative headline searches. Compare event statistics to rolling placebo dates 160 through 31 trading sessions before the event, re-estimating the same 220-session model with the same 30-session gap; use add-one empirical tail ranks and explicitly state non-exchangeability and overlapping-window limitations.

## Corporate news audit
Before main estimation, build an independently sourced earnings/material-news ledger for Aug 31-Sep 4. Full sample remains primary; sensitivity omits all firms with documented earnings releases or major investor/product announcements in Sep 2-4. Exclusion decisions use news timing only and are frozen before outcome estimation. Audit completeness limitations must be disclosed.

## Optional intraday extension
Acquire 5-minute bars if accessible to preserve a short-lived public-data opportunity, but do not treat them as confirmatory. Any intraday result requires verified actual announcement timing, timezone, regular-session coverage and a prespecified return construction. Without this gate, archive only and do not calculate event effects.

## Integrity and delivery
Never fabricate observations, references, author information, p values, or journal ranking. Missing data or failed source access is an explicit feasibility outcome. Report all two primary contrasts, even null or opposite signs. A top-quartile journal is an aspiration; independent novelty, identification, measurement and editorial assessment determine readiness. Full empirical manuscript requires verified input observations; if unavailable, produce a complete protocol manuscript with explicit unestimated results rather than simulated empirical findings.
