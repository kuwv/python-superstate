Superstate
==========

Robust statechart for configurable automation rules.


## How to use

A very simple example taken from specs.

```python
>>> from superstate import StateChart, state

>>> class SimpleMachine(StateChart):
...     __superstate__ = state(
...         {
...             'name': 'machine',
...             'initial': 'created',
...             'states': [
...                 {
...                     'name': 'created',
...                     'transitions': [
...                         {'event': 'queue', 'target': 'waiting'},
...                         {'event': 'cancel', 'target': 'canceled'},
...                     ],
...                 },
...                 {
...                     'name': 'waiting',
...                     'transitions': [
...                         {'event': 'process', 'target': 'processed'},
...                         {'event': 'cancel', 'target': 'canceled'},
...                     ]
...                 },
...                 {'name': 'processed'},
...                 {'name': 'canceled'},
...             ]
...         }
...     )

>>> machine = SimpleMachine()
>>> machine.state
'AtomicState(created)'

>>> machine.trigger('queue')
>>> machine.state
'AtomicState(waiting)'

>>> machine.trigger('process')
>>> machine.state
'AtomicState(processed)'

>>> cancel_machine = SimpleMachine()
>>> cancel_machine.state
'AtomicState(created)'

>>> cancel_machine.trigger('cancel')
>>> cancel_machine.state
'AtomicState(canceled)'

```


## States

A Superstate state machine must have one initial state and at least one other additional state.

A state may have pre and post callbacks, for running some code on state `on_entry`
and `on_exit`, respectively. These params can be method names (as strings),
callables, or lists of method names or callables.


## Transitions

Transitions lead the machine from a state to another. Transitions must have
both `event`, and `target` parameters. The `event` is the method that have to be
called to launch the transition. The `target` is the state to which the
transition will move the machine. This method is automatically created
by the Superstate engine.

A transition can have optional `action` and `cond` parameters. `action` is a
method (or callable) that will be called when transition is launched. If
parameters are passed to the event method, they are passed to the `action`
method, if it accepts these parameters. `cond` is a method (or callable) that
is called to allow or deny the transition, depending on the result of its
execution. Both `action` and `cond` can be lists.

The same event can be in multiple transitions, going to different states, having
their respective needs as selectors. For the transitions having the same event,
only one `cond` should return a true value at a time.


### Install

```
pip install superstate
```


### Test

```
tox
```


## Attribution

Superstate is forked from https://github.com/nsi-iff/fluidity created by Rodrigo Manhães.
