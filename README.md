\# Network Topology Identification – Round 1



This repository contains the preprocessing pipeline used to infer relative

network topology from cellular throughput statistics.



\## Motivation

Packet loss in the provided dataset is saturated for some cells and does not

reveal structural information. We therefore use \*\*relative throughput-drop–based

congestion events\*\* to capture shared fronthaul contention.



\## Pipeline

1\. Slot-level throughput aggregation per cell

2\. Congestion detection using rolling baseline throughput drops

3\. Construction of a multi-cell congestion event matrix

4\. Similarity-based topology inference (downstream)



\## Key Output

`data/multicell\_congestiondata.csv`



\*\*Columns\*\*

\- `slot\_id`

\- `cell\_id`

\- `congestion\_event` (binary)



This file is used to compute similarity matrices and infer shared network links.



