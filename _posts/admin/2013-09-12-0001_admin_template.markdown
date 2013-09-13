---
layout: endpoint
category: admin
title: /admin/template
type: READ
request: {"key": TEMPLATE_KEY}
response:   |
            {
                "status" : 0,
                "procName" : "admin_get_template",
                "Template" : TEMPLATE_DETAILS
            }
---

Returns all template details with tasks and services for a given template key. Template key is a unique identifier.