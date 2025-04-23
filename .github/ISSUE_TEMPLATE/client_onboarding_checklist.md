---
name: New Client Onboarding Checklist
about: A high level checklist to follow when onboarding a new client
title: '[CLIENT]: Onboarding Master GHI'
labels: ''
assignees: ''
---

**BACKGROUND:**
High level checklist for tracking YHP onboarding progress.

**SME Team:**
- [ ] Request ACO-MS CLI access as credential delegate and
- [ ] Sign BAA
- [ ] Activate ACO-MS
- [ ] Update calendar per notes
- [ ] Schedule when to load data
- [ ] Update [client_agreem_period](https://docs.google.com/spreadsheets/d/1EnDeMmON5Fb4oqCCd7te1zSfUlfomBV5VaEk1FtSvr4/edit#gid=346086450)
- [ ] Request roster (send [Rosters and Preferred Networks Data Request](https://docs.google.com/document/d/18cf50gkCdcnOuwO4dL74pLLhXvVFGjYqTj6RHZB9Iv4/edit))
- [ ] Request [APM entity QPP portal access](https://docs.google.com/document/d/1oVabeGbP0DnyMsVtJ9gsJn1-i5IPtySgA9WtC9giU6k/edit#heading=h.jw03woo0j5m5)
- [ ] Download ACO-MS files: [ACO-MS](https://docs.google.com/document/d/1oVabeGbP0DnyMsVtJ9gsJn1-i5IPtySgA9WtC9giU6k/edit#heading=h.jb3az89rop2m)
  - [ ] Participant lists 2020, 2021
  - [ ] Participant list 2022
  - [ ] Provider/supplier lists 2020, 2021
  - [ ] Provider/supplier list 2022
  - [ ] Participation options report (POR) 2020, 2021
  - [ ] Participation options report (POR) 2022
  - [ ] QPP Sources

**DE Team:**
- [ ] Intake data from ACOMS
  - [ ] Confirm ACOMS Data Hub access
  - [ ] Comfirm client_agreem_period population, if not updated in the database, run template `refresh_manual_gsheet_input.sql`
  - [ ] Create data folder on Florence `mkdir /data/{client}/`
  - [ ] Create a new ACOMS Data Hub CLI Key: `ACOMS -> API Credendtials -> Create New API Credentials -> (client name: "Master [n]", access level: "Credential Delegate", ACO: "Select ALL", IP: Nord and Florence IP [212.103.48.219, 13.58.128.89])`
  - [ ] Pass keys to config via `acoms-cli configure`, refresh config.txt by deleting it and re-running data_hub_api.py
  - [ ] (To kick off intake manually) From the folder `/data/in/` on Florence, run `python ~/Documents/vh-core/vh_core/data_hub_api.py`
- [ ] Open create_schemas script, change client variable, then run to initialze new schemas `scripts/create_schemas.py`
- [ ] Add the vldt_client_deliv gdrive folder link to `vh_core/config/gdrive_config.yml`
- [ ] Make sure the client has a vars file under `vh_core/config/`
- [ ] Create temporary fake custom roster
- [ ] Schedule Airflow DAGs
- [ ] Custom Roster Processing
