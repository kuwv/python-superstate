Provide simple example of a statechart.

```python
>>> from superstate import StateChart, state


>>> class SimpleMachine(StateChart):
...     __superstate__ = state(
...         {
...             'name': 'simple',
...             'initial': 'created',
...             'states': [
...                 {
...                     'name': 'created',
...                     'transitions': [
...                         {'event': 'queue', 'target': 'waiting'},
...                         {'event': 'cancel', 'target': 'cancelled'},
...                     ],
...                     'on_entry': lambda: print('created'),
...                 },
...                 {
...                     'name': 'waiting',
...                     'transitions': [
...                         {'event': 'process', 'target': 'processed'},
...                         {'event': 'cancel', 'target': 'cancelled'},
...                     ],
...                     'on_entry': lambda: print('waiting'),
...                 },
...                 {'name': 'processed', 'on_entry': lambda: print('processed')},
...                 {'name': 'cancelled', 'on_entry': lambda: print('cancelled')},
...             ],
...         }
...     )


```

```python
>>> machine = SimpleMachine(logging_enabled=True, logging_level='debug')
created

>>> machine.state
'AtomicState(created)'

```


```python
# machine.queue()
>>> machine.trigger('queue')
waiting

>>> machine.state
'AtomicState(waiting)'

```

```python
# machine.process()
>>> machine.trigger('process')
processed

>>> machine.state
'AtomicState(processed)'

```

```python
>>> cancel_machine = SimpleMachine()
created

>>> cancel_machine.state
'AtomicState(created)'

```

```python
# cancel_machine.cancel()
>>> cancel_machine.trigger('cancel')
cancelled

>>> cancel_machine.state
'AtomicState(cancelled)'

```
