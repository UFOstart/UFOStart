---
layout: endpoint
category: admin
title: /admin/service/all
type: READ
request: {}
response:   |
            {
                "status" : 0,
                "procName" : "admin_services_get",
                "Services" : [
                    {"name":..., "url":..., "logo":...}
                    ...
                ]
            }
---

Returns all services in the system.