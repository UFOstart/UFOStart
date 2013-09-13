---
layout: endpoint
category: admin
title: /admin/service/create
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
                "procName" : "admin_service_create"
            }

---

Add a new service to the system. `SERVICE_NAME` needs to be unique.

Possible dbMessage: `Service_Already_Exists`