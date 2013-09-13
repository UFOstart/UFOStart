---
layout: endpoint
category: admin
title: /admin/template/all
type: READ
request: {}
response:   |
            {
                "status" : 0,
                "procName" : "admin_get_templates",
                "Templates" : TEMPLATE_DETAILS_LIST
            }
---

Returns all templates in the system.