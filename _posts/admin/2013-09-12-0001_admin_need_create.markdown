---
layout: endpoint
category: admin
title: /admin/need/create
type: WRITE
request: |
        {
            "name" : DEFAULT_TASK_NAME,
            "summary" : FREETEXT_TASK_SUMMARY,
            "category" : "TECH|MISC|SALES|MARKETING|OPERATIONS",
            "Services" : [{
                "name" : SERVICE_NAME
            }],
            "Tags" : [{
                "name" : TAG_NAME
            }]
        }
response:   |
            {
                "status" : 0,
                "procName" : "admin_need_create"
            }

---

Create a new task-template.