---
layout: endpoint
category: admin
title: /admin/service/edit
type: WRITE
request: |
        {
            "name" : SERVICE_NAME,
            "url" : SERVICE_URL,
            "logo" : SERVICE_LOGO_URL
        }
response:   |
            {
                "status" : 0,
                "procName" : "admin_service_edit"
            }

---

Update service properties. Name is the unique identifier and thus cannot be changed.