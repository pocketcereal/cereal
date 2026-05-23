# Starting spec

For each of the items below we must define the programming patterns to use, implementation details, and structure to ensure long term maintainability and ease of extendability. Each of the top level sections should have clear acceptance criteria per element. This is not a concrete plan by any means. We are going to pick apart each item and write proper issues and track them.

## multiple sources

- Assert we can strem video from our usb camera in our preview window
  - We need to talk about the current source registeration and interface. We are building to handle multiple media formats. Right now we have single file modules and a simple prototype that reads from a file and now i want to extend our "media" module into further distinct interfaces that follow SOLID programming principles. Lets talk about how we register sources. currently, we have a config/*.yaml file that is the main config for sources. Lets focus in on the next one which is usb cameras or really any other media device. Lets grill with docs on that and come up with the next unit of work
