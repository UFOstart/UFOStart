---
layout: endpoint
category: endpoint
title: /web/template/list
type: READ
request: {}
response:   |
            {
                "status" : 0,
                "procName" : "user_get_templates",
                "Templates" : LIST_OF_TEMPLATES
            }

---

Returns list of all templates, complete with tasks, tags and services.