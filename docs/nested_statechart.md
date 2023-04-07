Provide nested statechart example to search transitions.

```python
>>> from superstate import StateChart, state


>>> class Example(StateChart):
... 
...     __superstate__ = state(
...         {
...             'name': 'example',
...             'initial': 'on',
...             'states': [
...                 {
...                     'name': 'on',
...                     'initial': 'high',
...                     'states': [
...                         {
...                             'name': 'low',
...                             'transitions': [
...                                 {'event': 'to_medium', 'target': 'medium'},
...                                 {
...                                     'event': 'stop',
...                                     'target': 'off',
...                                     'cond': lambda x: False,
...                                 },
...                             ],
...                         },
...                         {
...                             'name': 'medium',
...                             'transitions': [
...                                 {'event': 'to_low', 'target': 'low'},
...                                 {'event': 'to_high', 'target': 'high'},
...                                 {'event': 'stop', 'target': 'off'},
...                             ],
...                         },
...                         {
...                             'name': 'high',
...                             'transitions': [
...                                 {'event': 'to_medium', 'target': 'medium'},
...                                 {
...                                     'event': 'stop',
...                                     'target': 'off',
...                                     'cond': lambda x: False,
...                                 },
...                             ],
...                         },
...                     ],
...                 },
...                 {
...                     'name': 'off',
...                     'transitions': [{'event': 'start', 'target': 'on'}],
...                 },
...             ],
...             'transitions': [{'event': 'stop', 'target': 'off'}],
...         }
...     )


>>> example = Example()

```

Check that initial state is "on".

```python
>>> example.state
'CompoundState(on)'

```

Check that `process_transitions` returns only one transition.

```python
>>> example.process_transitions('stop')
'Transition(event=stop, target=off)'

```

Use `trigger` function to transition from "on" state to "off".
```python
>>> example.state
'CompoundState(on)'

>>> example.trigger('stop')
>>> example.state
'AtomicState(off)'

```

Get the name of the current state.

```python
>>> example.state.name
'off'

```
