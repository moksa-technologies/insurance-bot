---
layout: default
title: Customer SOP
---

{% capture sop_markdown %}
{% include_relative README.md %}
{% endcapture %}

{{ sop_markdown | markdownify }}

## Downloads
- [Customer SOP (Word)]({{ '/Customer_SOP.docx' | relative_url }})
