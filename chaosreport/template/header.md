---
title: {{title}}
date: {{today}}
---

\newpage

# Summary

This report aggregates {{num_experiments}} experiments spanning over the
following subjects:

{% for tag in tags %}{% if loop.last %}*{{tag}}*{% else %}*{{tag}}*, {% endif %}{% endfor %}

## Contributions 

Contributions surface the properties this collection of experiments
target in order to improve the confidence and trust in the system.

The aggregated {{num_experiments}} experiments cover
{{num_distinct_contributions}} distinct contributions:

{% if export_format not in ["html", "html5"] %}
![](data:image/png;base64,{{contribution_distribution}})
\ 

  {% else %}
<figure>
    {{contribution_distribution}}
</figure>
  {% endif %}

\newpage


The breakdown by contribution impact for each experiment[^1]:

{% if export_format not in ["html", "html5"] %}
![](data:image/png;base64,{{contributions}})
\ 

  {% else %}
<figure>
    {{contributions}}
</figure>
  {% endif %}

Sparse lines indicate a given experiment focused on a specific subset of
contributions.

Sparse columns indicate that a given contribution was seldom impacted by this
collection of experiments. 

[^1]: Empty dots indicate an experiment is explicitely not addressing a given
contribution while missing dots indicate no data for a given contribution.

\newpage

# Experiments

