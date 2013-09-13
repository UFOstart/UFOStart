---
layout: endpoint
category: endpoint
title: /web/need/invite
type: WRITE
request: |
        {
            "Invite" : {
                "companySlug" : COMPANY_SLUG <b>required</b>,
                "companyName" : COMPANY_NAME <b>required</b>,
                "invitorToken" : INVITOR_USER_TOKEN <b>required</b>,
                "invitorName" : INVITOR_NAME <b>required</b>,
                "name" : INVITEE_NAME <b>required</b>,
                "email" : INVITEE_EMAIL <b>required</b>,
                "Need" : {
                    "slug" : NEED_SLUG <b>required</b>,
                    "name" : NEED_NAME <b>required</b>
                }
            }
        }

response: {"status" : 0}

---

Invites a contact to a need.
