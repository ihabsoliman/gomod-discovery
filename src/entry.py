from js import Response


async def on_fetch(request, env):
    print("on_fetch called")
    return Response.new(env.MY_VARIABLE)
