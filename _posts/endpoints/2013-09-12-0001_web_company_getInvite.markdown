---
layout: endpoint
category: endpoint
title: /web/company/getInvite
type: READ
request:    |
            {"inviteToken": INVITE_TOKEN}
response:   |
            {
                "status" : 0,
                "procName" : "invite_get",
                "Invite" : {
                    "invitorName" : INVITOR_NAME,
                    "companySlug" : COMPANY_SLUG,
                    "companyName" : COMPANY_NAME,
                    "name" : INVITEE_NAME,
                    "inviteToken" : INVITE_TOKEN,
                    "role" : "TEAM_MEMBER|FOUNDER"
                }
            }

---

`inviteToken` is the token sent out to the Invitee, it uniquely identifies an invitation.
This endpoint returns the most basic information about an invitation based on `inviteToken`.