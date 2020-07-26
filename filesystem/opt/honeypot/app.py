#!/usr/bin/python3.8
import os
import json
import random
import asyncio
from asyncio import wait_for

from aiohttp import web
from hpfeeds.asyncio import ClientSession

from response_templates import file_contents, command_contents

HPFSERVER = os.environ.get("HPFSERVER", "127.0.0.1")
HPFPORT = int(os.environ.get("HPFPORT", 10000))
HPFIDENT = os.environ.get("HPFIDENT", "testing")
HPFSECRET = os.environ.get("HPFSECRET", "secretkey")
HIVEID = os.environ.get("HIVEID", "UnknownHive")


def html_response(text):
    return web.Response(text=str(text), content_type='text/html')


def json_response(text):
    return web.Response(text=text, content_type='application/json')


async def on_prepare(request, response):
    """Sets the Reponse Headers with some default values"""
    response.headers['Server'] = "Apache"
    response.headers['F5-Login-Page'] = "true"
    response.headers['Cache-Control'] = "no-cache, must-revalidate"
    response.headers['Connection'] = "Keep-Alive"
    response.headers['Pragma'] = "no-cache"
    response.headers['Content-Security-Policy'] = "default-src 'self'  'unsafe-inline' 'unsafe-eval' data: blob:; img-src 'self' data:  http://127.4.1.1 http://127.4.2.1"


    # then we create the log entry before we return the response object. 
    print("{0} request for {1}".format(request.method, request.path))

    # Get HTTP as version string
    http_version = "HTTP/{0}.{1}".format(request.version.major, request.version.minor)

    # convert Cookies to a standard dict, We will loose Duplicates
    http_cookies = {}
    for k, v in request.cookies.items():
        http_cookies[k] = v

    # convert Headers to a standard dict, We will loose Duplicates
    http_headers = {}
    for k, v in request.headers.items():
        http_headers[k] = v

    # convert POST to a standard dict, We will loose Duplicates
    http_post = {}
    if request.method == 'POST':
        data = await request.post()
        for key, value in data.items():
            http_post[key] = value

    event_message = {
        "hive_id": HIVEID,
        "source_ip": request.remote,
        "http_remote": request.remote,
        "http_host": request.host,
        "http_version": http_version,
        "http_method": request.method,
        "http_scheme": request.scheme,
        "http_query": request.path_qs,
        "http_post": http_post,
        "http_headers": http_headers,
        "http_path": request.path,
        "port": "443",
        "honeypot_type": "F5",
        "service": "HTTP"
    }

    # Send the Broker message
    # Set timeout to 3 seconds in a try: except so we dont kill the http response

    # Don't log favicon
    if not event_message['http_path'] == "/favicon.ico":
        try:
            await wait_for(hpfeeds_publish(event_message), timeout=3)
        except asyncio.TimeoutError:
            print("Unable to connect to hpfeeds broker.")
            pass


async def hpfeeds_publish(event_message):
    async with ClientSession(HPFSERVER, HPFPORT, HPFIDENT, HPFSECRET) as client:
        client.publish('f5.sessions', json.dumps(event_message).encode('utf-8'))
    return True


async def login_page(request):
    # page = request.match_info.get('name', "Anonymous")
    with open("login.jsp", "r+") as input_file:
        file_data = input_file.read()
        return html_response(file_data)
    #return web.FileResponse('./login.jsp')


async def file_save(request):
    # This is easy as we just return an empty data set. 
    # To really mess with people we are going to add whatever they send to our file object so they think its there :)
    file_name = ""
    content = ""
    if request.method == "POST":
        data = await request.post()
        try:
            file_name = data['fileName']
            content = data['content']
        except:
            pass
    elif request.method == "GET":
        try:
            file_name = request.rel_url.query['fileName']
            content = request.rel_url.query['content']
        except:
            pass

    if file_name.startswith(('/tmp/', '/shared/')):
        # Add their data to our array
        file_contents[file_name] = content
        response_data = ""

    else:
        # We can only write to certain paths
        with open("fileSaveError.html", "r+") as input_file:
            file_data = input_file.read()
            response_data = file_data.replace("FILEPATH", file_name)
        
    return html_response(response_data)


async def file_read(request):
    # This one is a file read request lets can some common responses and then a default 
    # This can be GET or POST so need to handle both. 

    file_name = ""
    if request.method == "POST":
        try:
            data = await request.post()
            file_name = data['fileName']
        except:
            pass
    elif request.method == "GET":
        try:
            file_name = request.rel_url.query['fileName']
        except:
            pass

    if file_name in file_contents:
        file_data = file_contents[file_name]
        response_data = json.dumps({"output": file_data})
    else:
        with open("fileReadError.html", "r+") as input_file:
            file_data = input_file.read()
            response_data = file_data.replace("FILEPATH", file_name)

    return html_response(response_data)


async def tmsh_cmd(request):
    # This one is a file read request lets can some common responses and then a default 
    # This can be GET or POST so need to handle both. 

    if request.method == "POST":
        try:
            data = await request.post()
            command = data['command']
        except:
            pass
    elif request.method == "GET":
        try:
            command = request.rel_url.query['command']
        except:
            pass

    command = command.replace("+", " ")

    if command in command_contents:
        file_data = command_contents[command]
        response_data = {"error": "", "output": file_data}
    else:
        response_data = {"error": "", "output": ""}

    return html_response(json.dumps(response_data))


app = web.Application()
app.on_response_prepare.append(on_prepare)

app.router.add_route('*', '/{name:.*/fileRead.jsp}', file_read)
app.router.add_route('*', '/{name:.*/fileSave.jsp}', file_save)
app.router.add_route('*', '/{name:.*/tmshCmd.jsp}', tmsh_cmd)

# All other pages return the login page as a 302
app.router.add_route('*', '/{name:.*}', login_page)

if __name__ == "__main__":
    web.run_app(app, port=8181)