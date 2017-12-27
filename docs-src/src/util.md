# Other utilities

hgf also provides various utilities that may be helpful but are not strictly necessary.


## Timer

In `hgf.util.timer` there are two classes, `Time`, `Timer`, and `CountdownTimer`.

The `Time` class represents a day, hour, month, second, millisecond tuple with attributes named `d`, `h`, `m`, `s`, `ms`, respectively. These attributes are properties, and changes to one of them will be distributed appropriately (including handling of non-integral values). `Time` objects may be added and subtracted.

**Known issue**: Negative time is not handled properly so it should be avoided when possible (though arithmetic with negative time will get the correct result).

The `Timer` class uses `Time` internally. It acts as a stopwatch that counts up from 0, with methods `start`, `pause`, `unpause`, `reset`, and `restart`. Note that `start` takes an optional argument allowing `Timer` to start at any `Time`.

The `CountdownTimer` class is a subclass of `Timer`. The only difference is that it counts *down* and then stops when it reaches 0.
