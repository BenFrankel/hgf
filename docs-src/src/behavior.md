# Behavior


hgf uses the [observer pattern](https://en.wikipedia.org/wiki/Observer_pattern) to separate interface from behavior. `hgf.model` provides the base class `Subject` to be inherited by any class modeling the behavior of a `StructuralComponent`. Every `Subject` can set a list of features (`self.state_properties`) that influence the external appearance of the `StructuralComponent`, so that it can be redrawn only when necessary.

For example, consider a `StructuralComponent` representing a card in a card game. The card can be face up or face down, and the player can select it. We can use a `Subject` to model this behavior:

```python
class Card(model.Subject):
    def __init__(self):
        super().__init__()
        
        self.selected = False
        self.face_up = True
        
        self.state_properties = 'selected', 'face_up'
    
    ...
```

Whenever the value of `selected` or `face_up` changes, the card will automatically be redrawn on screen. For any feature of the `Subject` that influences external appearance but doesn't have a corresponding attribute, you can define a property instead.

