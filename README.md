Superstate
==========

Compact statechart that can be vendored.


## How to use

A very simple example taken from specs.

```python
>>> from superstate import StateChart, create_machine

>>> class SimpleMachine(StateChart):
...     __machine__ = create_machine(
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
'State(created)'

>>> machine.queue()

>>> machine.state
'State(waiting)'

>>> machine.process()

>>> machine.state
'State(processed)'

>>> cancel_machine = SimpleMachine()

>>> cancel_machine.state
'State(created)'

>>> cancel_machine.cancel()

>>> cancel_machine.state
'State(canceled)'

```


## A slightly more complex example

For demonstrating more advanced capabilities::

```python
>>> from superstate import StateChart, create_machine

>>> class Relationship(StateChart):
...     __machine__ = create_machine(
...         {
...             'initial': 'dating',
...             'states': [
...                 {
...                     'name': 'dating',
...                     'transitions': [
...                         {
...                             'event': 'get_intimate',
...                             'target': 'intimate',
...                             'cond': 'drunk',
...                         }
...                     ],
...                     'on_entry': 'make_happy',
...                     'on_exit': 'make_depressed',
...                 },
...                 {
...                     'name': 'intimate',
...                     'transitions': [
...                         {
...                             'event': 'get_married',
...                             'target': 'married',
...                             'cond': 'willing_to_give_up_manhood',
...                         }
...                     ],
...                     'on_entry': 'make_very_happy',
...                     'on_exit': 'never_speak_again',
...                 },
...                 {
...                     'name': 'married',
...                     'on_entry': 'give_up_intimacy',
...                     'on_exit': 'buy_exotic_car',
...                 }
...             ]
...         }
...     )

...     def strictly_for_fun(self) -> None:
...         pass

...     def drunk(self) -> bool:
...         return True

...     def willing_to_give_up_manhood(self) -> bool:
...         return True

...     def make_happy(self) -> None:
...         pass

...     def make_depressed(self) -> None:
...         pass

...     def make_very_happy(self) -> None:
...         pass

...     def never_speak_again(self) -> None:
...         pass

...     def give_up_intimacy(self) -> None:
...         pass

...     def buy_exotic_car(self) -> None:
...         pass

# >>> relationship = Relationship()

```


## States

A Superstate state machine must have one initial state and at least one other additional state.

A state may have pre and post callbacks, for running some code on state *on_entry*
and *on_exit*, respectively. These params can be method names (as strings),
callables, or lists of method names or callables.


## Transitions

Transitions lead the machine from a state to another. Transitions must have
the *event*, and *target* parameters. The *event* is the method that have to be
called to launch the transition. The *target* is the state to which the
transition will move the machine. This method is automatically created
by the Superstate engine.

A transition can have optional *action* and *cond* parameters. *action* is a
method (or callable) that will be called when transition is launched. If
parameters are passed to the event method, they are passed to the *action*
method, if it accepts these parameters. *cond* is a method (or callable) that
is called to allow or deny the transition, depending on the result of its
execution. Both "action" and *cond* can be lists.

The same event can be in multiple transitions, going to different states, having
their respective needs as selectors. For the transitions having the same event,
only one *cond* should return a true value at a time.


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
