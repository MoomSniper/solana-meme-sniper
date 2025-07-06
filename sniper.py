  Using cached blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
Collecting certifi (from httpx==0.24.1->-r requirements.txt (line 2))
  Using cached certifi-2025.6.15-py3-none-any.whl.metadata (2.4 kB)
Collecting httpcore<0.18.0,>=0.15.0 (from httpx==0.24.1->-r requirements.txt (line 2))
  Using cached httpcore-0.17.3-py3-none-any.whl.metadata (18 kB)
Collecting idna (from httpx==0.24.1->-r requirements.txt (line 2))
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting sniffio (from httpx==0.24.1->-r requirements.txt (line 2))
  Using cached sniffio-1.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting asgiref>=3.2 (from Flask[async]==2.3.3->-r requirements.txt (line 1))
  Using cached asgiref-3.9.0-py3-none-any.whl.metadata (9.3 kB)
Collecting h11<0.15,>=0.13 (from httpcore<0.18.0,>=0.15.0->httpx==0.24.1->-r requirements.txt (line 2))
  Using cached h11-0.14.0-py3-none-any.whl.metadata (8.2 kB)
Collecting anyio<5.0,>=3.0 (from httpcore<0.18.0,>=0.15.0->httpx==0.24.1->-r requirements.txt (line 2))
  Using cached anyio-4.9.0-py3-none-any.whl.metadata (4.7 kB)
Collecting MarkupSafe>=2.0 (from Jinja2>=3.1.2->Flask==2.3.3->Flask[async]==2.3.3->-r requirements.txt (line 1))
  Using cached MarkupSafe-3.0.2-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.0 kB)
Using cached flask-2.3.3-py3-none-any.whl (96 kB)
Using cached httpx-0.24.1-py3-none-any.whl (75 kB)
Using cached python_telegram_bot-20.3-py3-none-any.whl (545 kB)
Using cached nest_asyncio-1.5.8-py3-none-any.whl (5.3 kB)
Using cached httpcore-0.17.3-py3-none-any.whl (74 kB)
Using cached anyio-4.9.0-py3-none-any.whl (100 kB)
Using cached h11-0.14.0-py3-none-any.whl (58 kB)
Using cached sniffio-1.3.1-py3-none-any.whl (10 kB)
Using cached asgiref-3.9.0-py3-none-any.whl (23 kB)
Using cached blinker-1.9.0-py3-none-any.whl (8.5 kB)
Using cached click-8.2.1-py3-none-any.whl (102 kB)
Using cached idna-3.10-py3-none-any.whl (70 kB)
Using cached itsdangerous-2.2.0-py3-none-any.whl (16 kB)
Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
Using cached MarkupSafe-3.0.2-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (23 kB)
Using cached werkzeug-3.1.3-py3-none-any.whl (224 kB)
Using cached certifi-2025.6.15-py3-none-any.whl (157 kB)
Installing collected packages: sniffio, nest_asyncio, MarkupSafe, itsdangerous, idna, h11, click, certifi, blinker, asgiref, Werkzeug, Jinja2, anyio, httpcore, Flask, httpx, python-telegram-bot
Successfully installed Flask-2.3.3 Jinja2-3.1.6 MarkupSafe-3.0.2 Werkzeug-3.1.3 anyio-4.9.0 asgiref-3.9.0 blinker-1.9.0 certifi-2025.6.15 click-8.2.1 h11-0.14.0 httpcore-0.17.3 httpx-0.24.1 idna-3.10 itsdangerous-2.2.0 nest_asyncio-1.5.8 python-telegram-bot-20.3 sniffio-1.3.1
==> Uploading build...
==> Uploaded in 3.5s. Compression took 1.6s
==> Build successful 🎉
==> Deploying...
==> Running 'python main.py'
INFO:httpx:HTTP Request: POST https://api.telegram.org/bot7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo/setWebhook "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.telegram.org/bot7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo/sendMessage "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: GET https://public-api.birdeye.so/defi/tokenlist?chain=solana "HTTP/1.1 200 OK"
Traceback (most recent call last):
  File "/opt/render/project/src/main.py", line 31, in <module>
    asyncio.run(setup())
    ~~~~~~~~~~~^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/nest_asyncio.py", line 31, in run
    return loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/nest_asyncio.py", line 99, in run_until_complete
    return f.result()
           ~~~~~~~~^^
  File "/usr/local/lib/python3.13/asyncio/futures.py", line 199, in result
    raise self._exception.with_traceback(self._exception_tb)
  File "/usr/local/lib/python3.13/asyncio/tasks.py", line 304, in __step_run_and_handle_result
    result = coro.send(None)
  File "/opt/render/project/src/main.py", line 20, in setup
    await monitor_market()
  File "/opt/render/project/src/sniper.py", line 57, in monitor_market
    selected = tokens[:3]
               ~~~~~~^^^^
KeyError: slice(None, 3, None)
==> Exited with status 1
==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
==> Running 'python main.py'
INFO:httpx:HTTP Request: POST https://api.telegram.org/bot7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo/setWebhook "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.telegram.org/bot7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo/sendMessage "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: GET https://public-api.birdeye.so/defi/tokenlist?chain=solana "HTTP/1.1 200 OK"
Traceback (most recent call last):
  File "/opt/render/project/src/main.py", line 31, in <module>
    asyncio.run(setup())
    ~~~~~~~~~~~^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/nest_asyncio.py", line 31, in run
    return loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.13/site-packages/nest_asyncio.py", line 99, in run_until_complete
    return f.result()
           ~~~~~~~~^^
  File "/usr/local/lib/python3.13/asyncio/futures.py", line 199, in result
    raise self._exception.with_traceback(self._exception_tb)
  File "/usr/local/lib/python3.13/asyncio/tasks.py", line 304, in __step_run_and_handle_result
    result = coro.send(None)
  File "/opt/render/project/src/main.py", line 20, in setup
    await monitor_market()
  File "/opt/render/project/src/sniper.py", line 57, in monitor_market
    selected = tokens[:3]
               ~~~~~~^^^^
KeyError: slice(None, 3, None)
