---
layout: endpoint
category: admin
title: /admin/static/set
type: WRITE
request: |
        {
          "Static" : [{
            "key" : "RoundDashboard.Help.Text",
            "value" : ""
          }]
        }
response:   |
            {
                "status" : 0,
                "procName" : "admin_static_set"
            }
---

Set the list of KEY/VALUE pairs. Needs to be the full list, as this overwrites existing content.