---
layout: endpoint
category: admin
title: /admin/need/edit
type: WRITE
request: |
        {
            "key" : UNIQUE_TASK_KEY,
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
                "procName" : "admin_need_edit"
            }

---

Edit a global task. The unique key is the identifying property.