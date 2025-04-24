name: 🧪 Pull Request Template
description: Standard PR checklist and changelog entry
title: "[PR]: <Brief description here>"
labels: ["engineering", "changelog"]
body:
  - type: markdown
    attributes:
      value: |
        **Description:**

        **Validations:**
        - [ ] Ran Genie  
          - [ ] Checked Atom + Vader output from Genie to ensure all tests are passing  
        - [ ] Ran Pytest (if applicable)  
        - [ ] Ran Tempest (if applicable)  

        > ℹ️ **Note for Tech:**  
        > If you complete **all the fields below**, this information will be automatically saved to a separate Markdown file for improved traceability.  
        > This helps **SMEs track product-impacting changes** more easily across releases.

  - type: textarea
    id: summary_of_changes
    attributes:
      label: 📝 Summary of Changes
      placeholder: Start here...
    validations:
      required: true

  - type: textarea
    id: impact_of_changes
    attributes:
      label: 💥 Impact of Changes
      placeholder: Start here...
    validations:
      required: true

  - type: dropdown
    id: affected_products
    attributes:
      label: 🧠 Affected Products
      multiple: true
      options:
        - "ACO Intelligence"
        - "ACU"
        - "Agreement Monitor"
        - "Apollo"
        - "Asteroid"
        - "Attribution Engine"
        - "Benchmarking"
        - "CCW Downloader"
        - "DataMart"
        - "DataOps"
        - "Giraffe"
        - "Infrastructure"
        - "Manual Intervention"
        - "Mercury"
        - "Metrics Engine"
        - "MSSP Tools"
        - "Netson"
        - "Observation Studio"
        - "Parsing"
        - "Pioneer"
        - "Provider Finder"
        - "Reggie"
        - "Reggie Competitor"
        - "Reggie Hypo"
        - "Scrappy"
        - "Tornado"
        - "Validation Engine"
        - "Hercules"
        - "Curif"
        - "Other"
    validations:
      required: false
