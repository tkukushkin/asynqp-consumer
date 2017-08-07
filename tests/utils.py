from asyncio import Future


def future(value=None, exception=None):
    f = Future()
    if exception:
        f.set_exception(exception)
    else:
        f.set_result(value)
    return f
