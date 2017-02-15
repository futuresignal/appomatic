
#delete {{submodule}}
curl -v -u username:password -i -X DELETE http://localhost:3000/api/{{config['api_version']}}/{{submodule}}/{id:[0-9]+}/