## {{experiment.title}}

{{experiment.description}}

### Summary
{% if export_format != "pdf" %}
{{experiment.title}}

{{experiment.description}}
{% endif %}

|                               |                     |
| ----------------------------- | ------------------- |
| **Status**                    | {{status}} |
| **Tagged**                    | {% for tag in experiment.tags %}{% if loop.last %}{{tag}}{% else %}{{tag}}, {% endif %}{% endfor %} |
| **Executed From**             | {{node}} |
| **Platform**                  | {{platform}} |
| **Started**                   | {{start | pretty_date}} | 
| **Completed**                 | {{end | pretty_date}} |
| **Duration**                  | {{pretty_duration(start, end)}} |

### Definition

The experiment was made of {{num_actions}} actions, to vary conditions in your
system, and {{num_probes}} probes, to collect objective data from your system
during the experiment.

{% if experiment.contributions %}

#### Organization Contributions

An estimate of relative system properties this experiment contributes to:

| Contribution     | Impact |
| ---------  | ------------------- |{% for c, w in experiment.contributions.items() %}
| {{c}} | {{w}} |{% endfor %}

The *"none"* value for an impact indicates that this experiment explicitely
does not address that specific property.

{% if export_format not in ["html", "html5"] %}
![](data:image/png;base64,{{experiment.contributions_chart}})
\ 

  {% else %}
<figure>
    {{experiment.contributions_chart}}
</figure>
  {% endif %}

{% endif %}

#### Steady State Hypothesis

{% if not hypo %}

No steady state hypothesis was defined in this experiment. This run was
exploratory.

{% else %}

The steady state hypothesis this experiment tried was
&ldquo;**{{hypo.title}}**&rdquo;.

##### Before Run

The steady state was {%if steady_states.before.steady_state_met %} verified {% else %} not verified. {% endif %}

|  Probe                                                         |  Tolerance                  | Verified |
| -------------------------------------------------------------- | --------------------------- | ------ | {% for probe in steady_states.before.probes %}
| {{probe.activity.name}}     | {{substitute(probe.activity.tolerance, True)}}         | {{probe.tolerance_met}} | {% endfor %}

##### After Run

The steady state was {%if steady_states.after.steady_state_met %} verified {% else %} not verified. {% endif %}

|  Probe                                                         |  Tolerance                  | Verified |
| -------------------------------------------------------------- | --------------------------- | ------ | {% for probe in steady_states.after.probes %}
| {{probe.activity.name}}     | {{substitute(probe.activity.tolerance, True)}}         | {{probe.tolerance_met}} | {% endfor %}

{% endif %}

#### Method

The experiment method defines the sequence of activities that help gathering
evidence towards, or against, the hypothesis.

The following activities were conducted as part of the experimental's method:

|  Type      |  Name                                                           |
| ---------- | --------------------------------------------------------------- | {% for activity in experiment.method %}
| {{activity.type}} | {{activity.name}} | {% endfor %}

### Result

The experiment was conducted on {{start|pretty_date}} and lasted roughly
{{pretty_duration(start, end)}}.

{% for item in run %}
#### {{item.activity.type | title}} - {{item.activity.name}}

|                       |               |
| --------------------- | ------------- |
| **Status**            | {{item.status}} |
| **Background**        | {{item.activity.get("background", False)}} |
| **Started**           | {{item.start | pretty_date}} | 
| **Ended**             | {{item.end | pretty_date}} |
| **Duration**          | {{pretty_duration(item.start, item.end)}} | {% if item.activity.get("pauses", {}).get("before") %}
| **Paused Before**     | {{substitute(item.activity.pauses.before)}}s | {% endif %} {% if item.activity.get("pauses", {}).get("after") %}
| **Paused After**      | {{substitute(item.activity.pauses.after)}}s | {% endif %}

The {{item.activity.type}} provider that was executed:

{% if item.activity.provider.type == "process" %}
|                 |                                                            |
| --------------- | ---------------------------------------------------------- |
| **Type**        | {{item.activity.provider.type}} |
| **Path**        | {{item.activity.provider.path}} |
| **Timeout**     | {{item.activity.provider.get("timeout", "N/A")}} | 
| **Arguments**   | {{substitute(item.activity.provider.get("arguments", "N/A"))}} | 
{% elif item.activity.provider.type == "http"  %}
|                 |                                                            |
| --------------- | ---------------------------------------------------------- |
| **Type**        | {{item.activity.provider.type}} |
| **URL**         | {{item.activity.provider.url}} |
| **Method**      | {{item.activity.provider.get("method", "GET")}} | 
| **Timeout**     | {{item.activity.provider.get("timeout", "N/A")}} | 
| **Arguments**   | {{substitute(item.activity.provider.get("arguments", "N/A"))}} | 
{% else %}
|                 |                                                            |
| --------------- | ---------------------------------------------------------- |
| **Type**        | {{item.activity.provider.type}} |
| **Module**      | {{item.activity.provider.module}} | 
| **Function**    | {{item.activity.provider.func}} | 
| **Arguments**   | {{substitute(item.activity.provider.get("arguments", "N/A"))}} | 
{% endif %}

{% if item.exception %}
The *{{item.activity.name}}* {{item.activity.type}} raised the following error
while running:

{% if export_format == "pdf" %}
```python
{{item.exception|join|wordwrap(70, break_long_words=False)}}
```
{% else %}
```python
{{item.exception|join}}
```
{% endif %}
{% endif %}

{%if item.text %}
  {% if export_format not in ["html", "html5"] %}
```
{{item.text}}
```

  {% else %}
<figure>
    {{item.text}}
</figure>
  {% endif %}
{% endif %}

{%if item.charts %}
{% for chart in item.charts %}
  {% if export_format not in ["html", "html5"] %}
![](data:image/png;base64,{{chart}})
\ 

  {% else %}
<figure>
    {{chart}}
</figure>
  {% endif %}
  {% endfor %}
{% endif %}

{% endfor %}

### Appendix

{% for item in run %}
#### {{item.activity.type | title}} - {{item.activity.name}}

The *{{item.activity.type}}* returned the following result:

```javascript
{{item.output | pprint}}
```

{% endfor %}