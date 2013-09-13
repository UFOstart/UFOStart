---
layout: endpoint
category: admin
title: /admin/template/create
type: WRITE
request: |
        {
          "name" : TEMPLATE_NAME <b>required</b>,
          "description" : FREETEXT_HTML_TEXT <b>required</b>,
          "picture" : TEMPLATE_PICTURE_URL <b>required</b>,
          "Need" : [
            {"name" : TASK_NAME},
            ...
          ] <b>required</b>,
          "active" : BOOLEAN <b>required</b>
        }
response:   |
            {
                "status" : 0,
                "procName" : "admin_template_create"
            }

---

Create new template.