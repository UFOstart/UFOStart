---
layout: endpoint
category: endpoint
title: /web/company/invite
type: WRITE
request:   |
           {
                "Invite" : [{
                    "companySlug" : COMPANY_SLUG,
                    "invitorToken" : INVITOR_USER_TOKEN,
                    "name" : INVITEE_NAME,
                    "invitorName" : INVITOR_NAME,
                    "role" : "TEAM_MEMBER|FOUNDER",
                    "email" : INVITEE_EMAIL
                }]
            }
response:   |
            {
                "status" : 0,
                "procName" : "company_invite"
            }

---

Invite a list of users to join the company. Invited users have status unconfirmed until they expressly accept the invitation. Calling this endpoint triggers sends a message to invitee with a unique `inviteToken`.