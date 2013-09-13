---
layout: endpoint
category: endpoint
title: /web/company/edit
type: WRITE
request:   |
            {
                "token" : FOUNDER_USER_TOKEN,
                "Company" : {
                    "name" :        COMPANY_NAME [required],
                    "logo" :        LOGO_PICTURE_URL [required],
                    "pitch" :       COMPANY_SHORT_PITCH [required],
                    "description" : COMPANY_LONG_DESCRIPTION [required],
                    "currency" :    {{ site.currency_label }} [required],
                    "slideShare" :  SLIDESHARE_URL,
                    "video" :       YOUTUBE_URL_or_VIMEO_URL,
                    "Pictures" :    LIST_OF_SLIDESHOW_PICTURES,
                    "Template" : {
                        "key" : SELECTED_TEMPLATE_KEY
                    }
                }
            }
response:   |
            {
                "status" : 0,
                "procName" : "company_create",
                "User" : FULL_USER_MODEL
            }

---

Updates company information, returns the Founder User with all his companies.