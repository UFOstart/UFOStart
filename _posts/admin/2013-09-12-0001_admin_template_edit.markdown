---
layout: endpoint
category: admin
title: /admin/template/edit
type: WRITE
request: |
        {
          "key": UNIQUE_TEMPLATE_KEY <b>required</b>,
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
                "procName" : "admin_template_edit"
            }

---

Edit existing template based on template key.