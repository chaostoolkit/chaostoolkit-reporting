---
title: {{title}}
date: {{today}}
---

\newpage

# Summary

This report aggregates {{num_experiments}} experiments spanning over the
following subjects:

{% for tag in tags %}{% if loop.last %}*{{tag}}*{% else %}*{{tag}}*, {% endif %}{% endfor %}

{% if contributions %}
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
### Experiment Contributions Breakdown
The breakdown of impacts each experiment contributes to for these system
properties[^1]:

{% if export_format not in ["html", "html5"] %}
![](data:image/png;base64,{{contributions_per_exp}})
\ 

  {% else %}
<figure>
    {{contributions_per_exp}}
</figure>
  {% endif %}

Sparse lines indicate a given experiment focused on a specific subset of
contributions.

Sparse columns indicate that a given contribution was seldom impacted by this
collection of experiments. 

\newpage
Another view of the same data:

{% if export_format not in ["html", "html5"] %}
![](data:image/png;base64,{{contributions_per_exp_radar}})
\ 

  {% else %}
<figure>
    {{contributions_per_exp_radar}}
</figure>
  {% endif %}

[^1]: Empty dots indicate an experiment is explicitely not addressing a given
contribution while missing dots indicate no data for a given contribution.

\newpage
### Areas Contributions Breakdown
The distribution of areas impacted by these contributions[^2]:

{% if export_format not in ["html", "html5"] %}
![](data:image/png;base64,{{contributions_per_tag}})
\ 

  {% else %}
<figure>
    {{contributions_per_tag}}
</figure>
  {% endif %}

Sparse lines indicate a given tag contributes only to a specific subset of
system property.

Sparse columns indicate that a given contribution impacts moderately areas
covered by the experiments.

[^2]: Empty dots indicate a tag is explicitely not addressing a given
contribution while missing dots indicate no data for a given contribution.

{% endif %}
\newpage
{% if num_experiments == 1 %}# Experiment
{%else%}# Experiments
{% endif %}
