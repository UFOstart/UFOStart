---
layout: endpoint
category: endpoint
title: /web/product/offer
type: WRITE
request: |
        {
            "Product" : {
                "token" : PRODUCT_TOKEN,
                "Offers" : [{
                    "name" : OFFER_NAME,
                    "description" : FREETEXT_DESCRIPTION,
                    "price" : PRICE_AMOUNT_INT,
                    "stock" : STOCK_AMOUNT_INT
                }]
            }
        }
response:   |
            {
                "status" : 0,
                "procName" : "company_product_offers",
                "Round" : ROUND_DETAILS
            }
---

Creates / updates a product's offers.