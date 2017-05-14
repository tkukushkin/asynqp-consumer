def future(value=None, exception=None):

    async def f():
        if exception:
            raise exception
        return value

    return f()
