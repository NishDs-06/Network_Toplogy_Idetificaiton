\# Topology Identification – Preprocessing Module



This module performs preprocessing for fronthaul network topology identification

based on congestion and packet loss correlation across cells.



\## Pipeline

1\. Symbol-level throughput → slot-level throughput

2\. Packet stats → loss events

3\. Throughput-based congestion detection

4\. Multi-cell congestion/loss matrix generation



\## Folder Structure

data/raw/          - Original Nokia logs  

data/processed/    - Slot \& multi-cell CSVs  

preprocessing/     - Python preprocessing scripts  

outputs/           - Intermediate / final outputs  



\## How to Run

```bash

pip install -r requirements.txt



python preprocessing/step2\_throughput\_to\_slot.py

python preprocessing/step3\_pktstats\_to\_loss.py

python preprocessing/step4\_merge\_cell1.py

python preprocessing/step4\_merge\_cell2.py

python preprocessing/step4\_merge\_cell3.py

python preprocessing/build\_multicell\_loss.py

python preprocessing/build\_multicell\_congestion.py



