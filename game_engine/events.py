class EventManager:
    def __init__(self):
        self._events = dict()

    def register(self, event_name, callback, err_callback=None):
        """
        Register an action to an event
        Args:
            event_name: name of the event
            callback: what will be called when the event is triggered
            err_callback: error callback if something went wrong. Must accept the error as argument.
        """
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append((callback, err_callback))

    def trigger(self, event_name, *params, **kwargs):
        """
        Triggers the event
        Args:
            event_name: name of the triggered event
            *params: additional parameters to send to the callback
            **kwargs: additional keyword arguments to send to the callback
        """
        if event_name in self._events:
            for callback, err_callback in self._events[event_name]:
                try:
                    callback(*params, **kwargs)
                except Exception as e:
                    if err_callback is not None:
                        err_callback(e)
                    else:
                        raise e
            self._events[event_name] = []

