# Configuration

External configuration and resources are handled by creating a context that automatically loads the default settings from a fixed directory. The context can also load other settings during runtime, to allow for things like customizable user configuration.

The context that handles these resources is called an `App`, which is spawned by an `AppManager`. The `AppManager` handles fixed/shared resources like images and sounds, while the `App` handles dynamic resources like style, options, and controls.

In general, data to be read by hgf should be written/stored in [JSON](https://en.wikipedia.org/wiki/JSON).


## Appdata

In order for hgf to know where to find an application's resources, there needs to be (in the same directory as your `main.py`) a folder named `appdata` with a subfolder named `appname`, where 'appname' is replaced by the name of your app. Within `appname` there should be a file `dir.json` that outlines the directories that hgf needs to look inside of. In particular:

<ul>
<li><code>"info"</code> directory, containing:</li>
<ul>
<li><code>fonts.json</code></li>
<li><code>images.json</code></li>
<li><code>music.json</code></li>
<li><code>sounds.json</code></li>
</ul>
<li><code>"config"</code> directory, containing:</li>
<ul>
<li><code>style.json</code></li>
<li><code>options.json</code></li>
<li><code>controls.json</code></li>
<li><code>resources.json</code></li>
</ul>
<li><code>"fonts"</code> directory, containing font files</li>
<li><code>"images"</code> directory, containing image files</li>
<li><code>"sounds"</code> directory, containing sound files</li>
<li><code>"music"</code> directory, containing music files</li>
</ul>

The purpose and format of the `.json` files listed above will be explained in the following sections.


### Style

`style.json` is structured as a collection of properties assigned to object types + their context. For example, the object type may be "button" and the property may be "font". The particular font could depend on the context that the button is in; if it's a main menu button, a dialog box button, etc.

**Note**: *object type* refers to a `StructuralComponent`'s `self.name` attribute, and *context* refers to either the `self.context` attribute or the parent's *context* (note that this is a recursive definition).

In order to reference a particular loaded resource, use `"$<resource-type>=<resource-name>"`. The value of `resource-name` is determined by configuration as detailed in the [Resources](#Resources) section.

Furthermore, it is possible to reference Python objects by using *style packs*. A style pack is a nested Python dictionary having the same structure (context, object type, properties) as `style.json`. The `AppManager` is provided with a dictionary of named style packs, and replaces `"@<style-pack-name>"` in `style.json` with the corresponding Python object.

Here is a simple example of a style configuration:

```json
{
  "default": {
    "default": {
      "font": "$font=default"
    },

    "window": {
      "bg-color": [0, 100, 160]
    }
  },

  "setgame": {
    "clock": {
      "font": "$font=digital-clock"
    }
  }
}
```

`"default"` is a special context / object type for when there is no special context, and can be overridden by properties in more specific context / object types.


### Options

`options.json` is structured the same way as `style.json`, but there is no way to reference loaded resources or Python objects. Otherwise the distinction is mostly semantic; options are meant to be settings not directly related to appearance, such as window size or an FPS limit.


### Controls

`controls.json` is a collection of key-bindings assigned to *messages* that are sent to and handled by the current `key_listener` in the hierarchy.

Here is a simple example of a controls configuration:

```json
{
  "global": {
    "exit": ["esc", "shift-q"]
  },

  "setgame": {
    "toggle-pause": ["p"],
    "restart": ["r"]
  }
}
```

`"global"` is a special context that is universal and that overrides all other bindings.


### Resources

The `fonts.json`, `images.json`, `music.json` and `sounds.json` files tell hgf what resources to load and what they should be called. The resources are loaded from the respective directories as outlined in `dir.json`. Here is an example for `fonts.json`:

```json
{
  "ubuntu mono": "UbuntuMono-R.ttf",
  "crysta": "Crysta.ttf"
  ...
}
```

Furthermore, resource aliases can be defined in `resources.json`. The first few files described create a layer of indirection so that resources can be loaded with a literal name that doesn't have to be changed if the filename changes, and `resources.json` creates a layer of indirection so that the same resource can fill different roles in the application.

For example, consider the following `resources.json` file:

```json
{
  "fonts": {
    "default": "ubuntu mono",
    "dialogue": "ubuntu mono",
    "digital-clock": "crysta"
  },

  "images": {
    ...
  },

  "sounds": {
    ...
  },

  "music": {
    ...
  }
}
```

`style.json` should reference resources through `resources.json`'s aliases.
