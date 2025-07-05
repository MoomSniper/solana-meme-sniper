telegram.error.Conflict: Conflict: can't use getUpdates method while webhook is active; use deleteWebhook to delete the webhook first
INFO:httpx:HTTP Request: POST https://api.telegram.org/bot7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo/getUpdates "HTTP/1.1 409 Conflict"
ERROR:telegram.ext.Updater:Error while getting Updates: Conflict: can't use getUpdates method while webhook is active; use deleteWebhook to delete the webhook first
ERROR:telegram.ext.Application:No error handlers are registered, logging exception.
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/ext/_updater.py", line 607, in _network_loop_retry
    if not await action_cb():
           ^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/ext/_updater.py", line 335, in polling_action_cb
    raise exc
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/ext/_updater.py", line 320, in polling_action_cb
    updates = await self.bot.get_updates(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<7 lines>...
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/ext/_extbot.py", line 543, in get_updates
    updates = await super().get_updates(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<9 lines>...
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/_bot.py", line 381, in decorator
    result = await func(self, *args, **kwargs)  # skipcq: PYL-E1102
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/_bot.py", line 3661, in get_updates
    await self._post(
    ^^^^^^^^^^^^^^^^^
    ...<7 lines>...
    ),
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/_bot.py", line 469, in _post
    return await self._do_post(
           ^^^^^^^^^^^^^^^^^^^^
    ...<6 lines>...
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/ext/_extbot.py", line 325, in _do_post
    return await super()._do_post(
           ^^^^^^^^^^^^^^^^^^^^^^^
    ...<6 lines>...
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/_bot.py", line 497, in _do_post
    return await request.post(
           ^^^^^^^^^^^^^^^^^^^
    ...<6 lines>...
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/request/_baserequest.py", line 168, in post
    result = await self._request_wrapper(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<7 lines>...
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/telegram/request/_baserequest.py", line 330, in _request_wrapper
    raise Conflict(message)
telegram.error.Conflict: Conflict: can't use getUpdates method while webhook is active; use deleteWebhook to delete the webhook first
Need better ways to work with logs? Try theRender CLIor set up a log stream integration 
